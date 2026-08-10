"""
Weather dashboard: human-facing UI for the same Open-Meteo data the Agent
Bricks agent sees through weather_mcp_server.py.

Deploy as its OWN Databricks App (separate from the MCP server) — same split
as Day 3's mcp_server/ + dashboard/. This app calls Open-Meteo directly via
its local copy of weather_broker.py (each Databricks App deploys from its own
folder).

Run locally:
    python app.py
"""

from __future__ import annotations

import os

from flask import Flask, jsonify, render_template, request

import weather_broker

app = Flask(__name__)

DEFAULT_LOCATION = os.environ.get("DEFAULT_LOCATION", "Chicago, IL")


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.errorhandler(Exception)
def handle_exception(err):
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


@app.route("/")
def index():
    return render_template("index.html", default_location=DEFAULT_LOCATION)


@app.route("/api/current")
def api_current():
    location = request.args.get("location", DEFAULT_LOCATION)
    try:
        return jsonify(weather_broker.get_current_conditions(location))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/forecast")
def api_forecast():
    location = request.args.get("location", DEFAULT_LOCATION)
    days = int(request.args.get("days", 5))
    try:
        return jsonify(weather_broker.get_forecast(location, days))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/recommendation")
def api_recommendation():
    location = request.args.get("location", DEFAULT_LOCATION)
    date = request.args.get("date") or None
    try:
        return jsonify(weather_broker.get_travel_recommendation(location, date))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", os.getenv("DATABRICKS_APP_PORT", "8001")))
    app.run(debug=False, host=host, port=port)
