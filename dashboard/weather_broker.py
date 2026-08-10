"""
Open-Meteo weather adapter for the weather-forecast MCP server.

Mirrors the role of alpaca_broker.py in Day 3: all HTTP calls and response
parsing live here so the @mcp.tool wrappers in weather_mcp_server.py stay thin.

Open-Meteo needs no API key (geocoding + forecast). If you swap in a keyed
provider (e.g. WeatherAPI.com), add Databricks secret lookup here using the
same _secret() / WorkspaceClient().secrets.get_secret() pattern as
alpaca_broker.py — never hardcode keys.
"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Any

import requests

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
NWS_ALERTS_URL = "https://api.weather.gov/alerts/active"
TIMEOUT = 20

# WMO weather interpretation codes → short human-readable labels.
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    77: "Snow grains",
    80: "Light rain showers",
    81: "Rain showers",
    82: "Violent rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm with hail",
}

# Travel-recommendation thresholds (tunable via app.yaml / env without
# changing tool signatures).
UMBRELLA_THRESHOLD_PCT = int(os.environ.get("UMBRELLA_THRESHOLD_PCT", "40"))
LIGHT_JACKET_LOW_F = int(os.environ.get("LIGHT_JACKET_LOW_F", "65"))
WARM_JACKET_LOW_F = int(os.environ.get("WARM_JACKET_LOW_F", "50"))


def _describe(code: int | None) -> str:
    if code is None:
        return "Unknown"
    return WMO_CODES.get(int(code), f"Unknown (WMO {code})")


def _is_number(text: str) -> bool:
    try:
        float(text)
        return True
    except (TypeError, ValueError):
        return False


def resolve_location(location: str) -> dict[str, Any]:
    """Resolve a place name or 'lat,lon' string to coordinates + display name.

    Raises:
        ValueError: if the location cannot be geocoded.
    """
    raw = str(location).strip()
    if not raw:
        raise ValueError("Location is required (city name or 'lat,lon').")

    parts = [p.strip() for p in raw.split(",")]
    if len(parts) == 2 and _is_number(parts[0]) and _is_number(parts[1]):
        return {
            "name": raw,
            "latitude": float(parts[0]),
            "longitude": float(parts[1]),
            "country_code": None,
        }

    # Prefer the full string for geocoding ("Austin, TX"); fall back to city.
    query = raw
    resp = requests.get(
        GEOCODE_URL,
        params={"name": query, "count": 1},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    results = resp.json().get("results") or []

    if not results and len(parts) > 1:
        resp = requests.get(
            GEOCODE_URL,
            params={"name": parts[0], "count": 1},
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []

    if not results:
        raise ValueError(
            f"Could not resolve location {location!r}. "
            "Try a clearer city name (e.g. 'Chicago, IL') or 'lat,lon'."
        )

    hit = results[0]
    label = ", ".join(
        x for x in (hit.get("name"), hit.get("admin1"), hit.get("country_code")) if x
    )
    return {
        "name": label,
        "latitude": hit["latitude"],
        "longitude": hit["longitude"],
        "country_code": hit.get("country_code"),
    }


def get_current_conditions(location: str) -> dict[str, Any]:
    """Current temperature, conditions, humidity, and wind for a location."""
    geo = resolve_location(location)
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "timezone": "auto",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "current": (
                "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                "weather_code,precipitation"
            ),
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    current = resp.json()["current"]
    return {
        "location": geo["name"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "temperature_f": current["temperature_2m"],
        "conditions": _describe(current.get("weather_code")),
        "humidity_pct": current["relative_humidity_2m"],
        "wind_mph": current["wind_speed_10m"],
        "precipitation_mm": current.get("precipitation"),
        "as_of": current.get("time"),
    }


def get_forecast(location: str, days: int = 5) -> dict[str, Any]:
    """Multi-day daily forecast (high/low, precip chance, conditions)."""
    days = max(1, min(int(days), 16))
    geo = resolve_location(location)
    resp = requests.get(
        FORECAST_URL,
        params={
            "latitude": geo["latitude"],
            "longitude": geo["longitude"],
            "timezone": "auto",
            "temperature_unit": "fahrenheit",
            "forecast_days": days,
            "daily": (
                "temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,weather_code"
            ),
        },
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    daily = resp.json()["daily"]
    forecast = [
        {
            "date": daily["time"][i],
            "high_f": daily["temperature_2m_max"][i],
            "low_f": daily["temperature_2m_min"][i],
            "precip_chance_pct": daily["precipitation_probability_max"][i],
            "conditions": _describe(daily["weather_code"][i]),
        }
        for i in range(len(daily["time"]))
    ]
    return {
        "location": geo["name"],
        "latitude": geo["latitude"],
        "longitude": geo["longitude"],
        "forecast": forecast,
    }


def _parse_target_date(raw: str | None, forecast_days: list[dict]) -> dict:
    """Pick a forecast day for a YYYY-MM-DD date, 'today', 'tomorrow', or None."""
    if not forecast_days:
        raise ValueError("Forecast is empty.")

    if raw is None or str(raw).strip() == "":
        # Prefer tomorrow when available; otherwise the first forecast day.
        if len(forecast_days) > 1:
            return forecast_days[1]
        return forecast_days[0]

    token = str(raw).strip().lower()
    today = date.today()
    if token in ("today",):
        target = today.isoformat()
    elif token in ("tomorrow",):
        target = (today + timedelta(days=1)).isoformat()
    else:
        # Validate ISO date.
        try:
            datetime.strptime(token, "%Y-%m-%d")
        except ValueError as exc:
            raise ValueError(
                f"Invalid date {raw!r}. Use YYYY-MM-DD, 'today', or 'tomorrow'."
            ) from exc
        target = token

    match = next((d for d in forecast_days if d["date"] == target), None)
    if match is None:
        available = f"{forecast_days[0]['date']} to {forecast_days[-1]['date']}"
        raise ValueError(
            f"No forecast available for {target}. Available range: {available}."
        )
    return match


def get_travel_recommendation(location: str, date: str | None = None) -> dict[str, Any]:
    """Derived packing advice from forecast thresholds (not a raw passthrough).

    Rules applied:
      - umbrella_needed when precip_chance_pct > UMBRELLA_THRESHOLD_PCT (40)
      - jacket: "warm" if low_f < 50, "light" if low_f < 65, else "none"
    """
    data = get_forecast(location, days=16)
    day = _parse_target_date(date, data["forecast"])

    precip = day.get("precip_chance_pct")
    low_f = day.get("low_f")
    high_f = day.get("high_f")

    umbrella_needed = precip is not None and precip > UMBRELLA_THRESHOLD_PCT
    if low_f is None:
        jacket = "unknown"
    elif low_f < WARM_JACKET_LOW_F:
        jacket = "warm"
    elif low_f < LIGHT_JACKET_LOW_F:
        jacket = "light"
    else:
        jacket = "none"

    parts = [
        f"On {day['date']} in {data['location']}: high {high_f}°F / low {low_f}°F, "
        f"{day['conditions']}, {precip}% chance of precipitation."
    ]
    if umbrella_needed:
        parts.append(
            f"Bring an umbrella (precip {precip}% > {UMBRELLA_THRESHOLD_PCT}% threshold)."
        )
    else:
        parts.append(
            f"Umbrella not required (precip {precip}% ≤ {UMBRELLA_THRESHOLD_PCT}% threshold)."
        )

    if jacket == "warm":
        parts.append(f"Wear a warm jacket (overnight low {low_f}°F < {WARM_JACKET_LOW_F}°F).")
    elif jacket == "light":
        parts.append(
            f"A light jacket is recommended (overnight low {low_f}°F < {LIGHT_JACKET_LOW_F}°F)."
        )
    elif jacket == "none":
        parts.append(
            f"No jacket needed for overnight lows around {low_f}°F "
            f"(≥ {LIGHT_JACKET_LOW_F}°F)."
        )

    return {
        "location": data["location"],
        "date": day["date"],
        "high_f": high_f,
        "low_f": low_f,
        "precip_chance_pct": precip,
        "conditions": day["conditions"],
        "umbrella_needed": umbrella_needed,
        "umbrella_threshold_pct": UMBRELLA_THRESHOLD_PCT,
        "jacket": jacket,
        "recommendation": (
            f"{'Bring an umbrella' if umbrella_needed else 'Skip the umbrella'}; "
            f"jacket={jacket}."
        ),
        "reasoning": " ".join(parts),
    }


def compare_locations(locations: list[str], days: int = 3) -> dict[str, Any]:
    """Side-by-side forecast summaries for multiple cities (stretch tool)."""
    if not locations:
        raise ValueError("Provide at least one location to compare.")
    cleaned = [str(x).strip() for x in locations if str(x).strip()]
    if not cleaned:
        raise ValueError("Provide at least one non-empty location.")
    if len(cleaned) > 5:
        raise ValueError("Compare at most 5 locations at a time.")

    comparisons = []
    errors = []
    for loc in cleaned:
        try:
            forecast = get_forecast(loc, days=days)
            comparisons.append(forecast)
        except Exception as exc:  # noqa: BLE001 - surface per-city failures cleanly
            errors.append({"location": loc, "error": str(exc)})

    return {
        "days_requested": days,
        "comparisons": comparisons,
        "errors": errors,
    }


def get_severe_weather_alerts(location: str) -> dict[str, Any]:
    """US severe-weather alerts via the National Weather Service API (stretch).

    NWS is US-only and requires no API key. Non-US locations return a clear
    message rather than inventing alerts.
    """
    geo = resolve_location(location)
    country = (geo.get("country_code") or "").upper()
    if country and country != "US":
        return {
            "location": geo["name"],
            "supported": False,
            "alerts": [],
            "message": (
                "NWS alerts are US-only. Resolved location is outside the US "
                f"({country or 'unknown country'})."
            ),
        }

    headers = {
        "User-Agent": "weather-mcp-server/1.0 (tidke.sandeep4@gmail.com)",
        "Accept": "application/geo+json",
    }
    resp = requests.get(
        NWS_ALERTS_URL,
        params={"point": f"{geo['latitude']},{geo['longitude']}"},
        headers=headers,
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    features = resp.json().get("features") or []
    alerts = []
    for feature in features[:10]:
        props = feature.get("properties") or {}
        alerts.append(
            {
                "event": props.get("event"),
                "severity": props.get("severity"),
                "headline": props.get("headline"),
                "onset": props.get("onset"),
                "ends": props.get("ends"),
                "description": (props.get("description") or "")[:500],
            }
        )

    return {
        "location": geo["name"],
        "supported": True,
        "alert_count": len(alerts),
        "alerts": alerts,
        "message": "No active NWS alerts for this point." if not alerts else None,
    }
