# Weather-Prediction MCP Server + Agent

Day 3 homework: a weather-forecast **MCP server** (FastMCP) plus Agent Bricks
config so an agent can answer natural-language weather questions.
Patterned after Day 3's `mcp_server/` + `dashboard/` Alpaca split
([databricks-lakebase-app-day-3](https://github.com/EcZachly/databricks-lakebase-app-day-3))
— reference pattern, not a verbatim copy.

**Author:** Sandeep Tidke  
**Repo:** https://github.com/tidkesandeep/weather-mcp-server  
**Branches:** `main`, `develop` (in sync)

## Requirements status

| Requirement | Status |
|-------------|--------|
| FastMCP server, streamable HTTP, `@mcp.tool` | Done — `mcp_server/weather_mcp_server.py` |
| Broker/adapter (no raw HTTP inside tools) | Done — `mcp_server/weather_broker.py` |
| ≥3 tools: current / forecast / prediction | Done (+2 stretch) |
| `app.yaml` + `requirements.txt` MCP app | Done |
| Free weather API, no secrets in git | Done — Open-Meteo (keyless) + NWS stretch |
| Clean errors (no stack traces to agent) | Done — `{"status":"error","message":...}` |
| Agent system prompt + tool list | Done — `agent/` |
| README + submission with demos | Done — this file + `SUBMISSION.md` |
| Deployed Databricks App (MCP) | Done — `mcp-weather-forecast` RUNNING |
| GitHub ↔ Databricks source sync | Done — byte-identical at last deploy |
| Agent Bricks / Playground registration | **UI step** — paste `/mcp` URL + system prompt (see below) |
| Optional dashboard Databricks App | Code ready in `dashboard/`; not deployed (workspace 3-app limit) |

## Architecture

```
Agent Bricks / AI Playground
        |  MCP (streamable HTTP)
        v
mcp_server/weather_mcp_server.py   ← Databricks App: mcp-weather-forecast
        |
        v
weather_broker.py
        ├── Open-Meteo geocoding
        ├── Open-Meteo forecast/current
        └── NWS alerts (US stretch)

dashboard/app.py  (optional human UI; own broker copy — not deployed yet)
```

## Live deployment (this workspace)

| Item | Value |
|------|-------|
| Workspace | https://dbc-da72c144-83db.cloud.databricks.com/ |
| App name | `mcp-weather-forecast` |
| App URL | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Workspace source | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` |
| Git folder | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server-repo` → `develop` |

## Weather API + auth

| API | Purpose | Auth |
|-----|---------|------|
| [Open-Meteo](https://open-meteo.com/) geocoding + forecast | Current + multi-day | None |
| [NWS](https://www.weather.gov/documentation/services-web-api) alerts | US severe weather (stretch) | None (User-Agent only) |

No Databricks secrets required. Do not commit API keys.

## Tools

| Tool | Capability |
|------|------------|
| `get_current_weather(location)` | Temp °F, conditions, humidity, wind |
| `get_forecast(location, days)` | Daily high/low, precip chance, conditions (1–16) |
| `get_travel_recommendation(location, date)` | **Derived** umbrella + jacket advice |
| `compare_locations(locations, days)` | Stretch — side-by-side forecasts |
| `get_severe_weather_alerts(location)` | Stretch — US NWS active alerts |

### Prediction logic (`get_travel_recommendation`)

Tunable via `mcp_server/app.yaml` env:

- **Umbrella** if `precip_chance_pct > UMBRELLA_THRESHOLD_PCT` (default 40)
- **Jacket** = `warm` if `low_f < 50`, `light` if `low_f < 65`, else `none`
- Returns flags plus a human-readable `reasoning` string

## Repository layout

```
mcp_server/     # Databricks App source for mcp-weather-forecast
dashboard/      # Optional stretch UI (code complete; slot-limited)
agent/          # SYSTEM_PROMPT.md + AGENT_CONFIG.md
docs/demos/     # Captured tool outputs
SUBMISSION.md   # Checklist, URLs, NL demos
README.md
```

## Local setup

```bash
cd mcp_server
pip install -r requirements.txt
python test_weather.py
python weather_mcp_server.py    # MCP on :8000 (path /mcp)
```

```bash
cd dashboard
pip install -r requirements.txt
python app.py                   # UI on :8001
```

## Sync GitHub ↔ Databricks App

```bash
export DATABRICKS_HOST=https://dbc-da72c144-83db.cloud.databricks.com
export DATABRICKS_TOKEN=<pat>

databricks sync --full . /Users/sandeeptidke.work@gmail.com/weather-mcp-server
databricks apps deploy mcp-weather-forecast \
  --source-code-path /Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/mcp_server \
  --mode SNAPSHOT
databricks repos update /Users/sandeeptidke.work@gmail.com/weather-mcp-server-repo --branch develop
```

## Register MCP + Agent Bricks (UI)

1. **AI Playground** → tools-enabled model → **Add tool → MCP Servers** →  
   `https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp`
2. Or **AI Gateway → MCPs → Register** (Unity Catalog MCP Service) with the same URL.
3. **Agents → Agent Bricks → Create agent** (Custom LLM).
4. Attach MCP tools; paste [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md).
5. Evaluate with prompts in [`agent/AGENT_CONFIG.md`](agent/AGENT_CONFIG.md).

## Demo questions

1. What's the weather in Chicago right now?
2. Will it rain in Austin this weekend?
3. Should I bring a jacket and umbrella to Seattle tomorrow?

Live tool outputs + agent-style answers: [`SUBMISSION.md`](SUBMISSION.md).

## License / data use

Open-Meteo non-commercial free tier (~10k calls/day). NWS data is public domain.
