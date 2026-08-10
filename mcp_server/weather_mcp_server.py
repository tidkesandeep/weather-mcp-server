"""
Weather-forecast MCP server.

Exposes weather tools over MCP (Model Context Protocol) so a Databricks
Agent Bricks agent can call them like any other tool:
    - get_current_weather(location)
    - get_forecast(location, days)
    - get_travel_recommendation(location, date)
    - compare_locations(locations, days)          [stretch]
    - get_severe_weather_alerts(location)         [stretch]

Backed by Open-Meteo (and optionally NWS for US alerts) via weather_broker.py.
Follows the same FastMCP + streamable-HTTP pattern as Day 3's
mcp_server/alpaca_mcp_server.py so it deploys as a Databricks App the same way.

Run locally:
    python weather_mcp_server.py
"""

from __future__ import annotations

import logging
import os

from fastmcp import FastMCP

import weather_broker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather-mcp-server")

mcp = FastMCP("weather-forecast")


@mcp.tool
def get_current_weather(location: str) -> dict:
    """
    Get current temperature, conditions, humidity, and wind for a location.

    Args:
        location: City name (e.g. "Chicago" or "Austin, TX") or a "lat,lon"
            string (e.g. "30.27,-97.74").

    Returns:
        A dict with location, temperature_f, conditions, humidity_pct,
        wind_mph, precipitation_mm, and as_of. On failure, returns
        {"status": "error", "message": ...} instead of raising.
    """
    try:
        result = weather_broker.get_current_conditions(location)
        result["status"] = "success"
        return result
    except Exception as exc:  # noqa: BLE001 - MCP tools must return clean errors
        logger.exception("get_current_weather failed for %r", location)
        return {"status": "error", "message": str(exc)}


@mcp.tool
def get_forecast(location: str, days: int = 5) -> dict:
    """
    Get a multi-day daily forecast for a location.

    Args:
        location: City name or "lat,lon" string.
        days: Number of days ahead to return (clamped to 1..16; default 5).

    Returns:
        A dict with location and forecast (list of date, high_f, low_f,
        precip_chance_pct, conditions). On failure, returns
        {"status": "error", "message": ...}.
    """
    try:
        result = weather_broker.get_forecast(location, days)
        result["status"] = "success"
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("get_forecast failed for %r", location)
        return {"status": "error", "message": str(exc)}


@mcp.tool
def get_travel_recommendation(location: str, date: str = "") -> dict:
    """
    Recommend packing (umbrella + jacket) for a location/date.

    This is a derived judgment call — not a raw API passthrough. It pulls the
    forecast, selects the target day, and applies explicit thresholds:
      - umbrella_needed when precip_chance_pct > 40
      - jacket="warm" if low_f < 50, "light" if low_f < 65, else "none"

    Args:
        location: City name or "lat,lon" string.
        date: Target day as YYYY-MM-DD, "today", "tomorrow", or empty
            (defaults to tomorrow when available).

    Returns:
        A dict with location, date, temps, precip_chance_pct, umbrella_needed,
        jacket, recommendation, and reasoning. On failure,
        {"status": "error", "message": ...}.
    """
    try:
        target = date.strip() or None
        result = weather_broker.get_travel_recommendation(location, target)
        result["status"] = "success"
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("get_travel_recommendation failed for %r", location)
        return {"status": "error", "message": str(exc)}


@mcp.tool
def compare_locations(locations: list[str], days: int = 3) -> dict:
    """
    Compare multi-day forecasts across up to 5 locations (stretch tool).

    Args:
        locations: List of city names or "lat,lon" strings.
        days: Forecast length per location (1..16; default 3).

    Returns:
        A dict with comparisons (successful forecasts) and errors (per-city
        failures). On total failure, {"status": "error", "message": ...}.
    """
    try:
        result = weather_broker.compare_locations(locations, days)
        result["status"] = "success"
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("compare_locations failed")
        return {"status": "error", "message": str(exc)}


@mcp.tool
def get_severe_weather_alerts(location: str) -> dict:
    """
    Fetch active US severe-weather alerts from the National Weather Service.

    Stretch tool. NWS covers US locations only; non-US lookups return a clear
    unsupported message rather than guessing.

    Args:
        location: City name or "lat,lon" string.

    Returns:
        A dict with location, supported, alert_count, and alerts list.
        On failure, {"status": "error", "message": ...}.
    """
    try:
        result = weather_broker.get_severe_weather_alerts(location)
        result["status"] = "success"
        return result
    except Exception as exc:  # noqa: BLE001
        logger.exception("get_severe_weather_alerts failed for %r", location)
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    # Databricks Apps route external HTTP traffic to this port via app.yaml;
    # streamable HTTP is the transport Databricks' MCP client/gateway expects.
    # Keep FastMCP's default /mcp mount path for Playground discovery.
    port = int(os.getenv("DATABRICKS_APP_PORT", os.getenv("PORT", "8000")))
    mcp.run(transport="http", host="0.0.0.0", port=port)
