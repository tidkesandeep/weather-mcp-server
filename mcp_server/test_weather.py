#!/usr/bin/env python
"""Smoke tests for weather_broker. Run before deploying:

    python test_weather.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import weather_broker


def test_current_conditions() -> bool:
    print("\n=== get_current_conditions('Chicago') ===")
    try:
        result = weather_broker.get_current_conditions("Chicago")
        assert "temperature_f" in result
        assert "conditions" in result
        print(f"OK: {result}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        return False


def test_forecast() -> bool:
    print("\n=== get_forecast('Austin, TX', days=5) ===")
    try:
        result = weather_broker.get_forecast("Austin, TX", days=5)
        assert len(result["forecast"]) == 5
        print(f"OK: {result['location']}, {len(result['forecast'])} days")
        for day in result["forecast"]:
            print(f"  {day}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        return False


def test_travel_recommendation() -> bool:
    print("\n=== get_travel_recommendation('Seattle', 'tomorrow') ===")
    try:
        result = weather_broker.get_travel_recommendation("Seattle", "tomorrow")
        assert "umbrella_needed" in result
        assert "jacket" in result
        assert "reasoning" in result
        print(f"OK: {result}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        return False


def test_bad_location() -> bool:
    print("\n=== bad location (expect clean ValueError) ===")
    try:
        weather_broker.get_current_conditions("Nowhereville, Atlantis")
        print("FAILED: expected ValueError")
        return False
    except ValueError as exc:
        print(f"OK: raised cleanly — {exc}")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: wrong exception type: {type(exc).__name__}: {exc}")
        return False


def test_compare_locations() -> bool:
    print("\n=== compare_locations(['Chicago', 'Austin'], days=2) ===")
    try:
        result = weather_broker.compare_locations(["Chicago", "Austin"], days=2)
        assert len(result["comparisons"]) == 2
        print(f"OK: compared {len(result['comparisons'])} cities")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}")
        return False


def main() -> bool:
    print("=" * 60)
    print("Weather Broker Test Suite")
    print("=" * 60)
    results = [
        test_current_conditions(),
        test_forecast(),
        test_travel_recommendation(),
        test_bad_location(),
        test_compare_locations(),
    ]
    print("\n" + "=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    return all(results)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
