# Weather-Prediction MCP Server + Agent

Day 3 homework: a weather-forecast **MCP server** (FastMCP) plus Agent Bricks
config so an agent can answer natural-language weather questions.
Patterned after Day 3's `mcp_server/` + `dashboard/` Alpaca split
([databricks-lakebase-app-day-3](https://github.com/EcZachly/databricks-lakebase-app-day-3))
— reference pattern, not a verbatim copy.

**Author:** Sandeep Tidke  
**Repo:** https://github.com/tidkesandeep/weather-mcp-server  
**Branches:** `main`, `develop` (kept in sync)

## Requirements status

| Requirement | Status |
|-------------|--------|
| FastMCP server, streamable HTTP, `@mcp.tool` | Done — `mcp_server/weather_mcp_server.py` |
| Broker/adapter (no raw HTTP inside tools) | Done — `shared/weather_broker.py` (synced into apps) |
| ≥3 tools: current / forecast / prediction | Done (+2 stretch) |
| HTTP retries/backoff + geocode cache | Done |
| `app.yaml` + `requirements.txt` MCP app | Done |
| Free weather API, no secrets in git | Done — Open-Meteo + NWS |
| Clean errors (`status=error`) | Done |
| Agent system prompt | Done — `agent/SYSTEM_PROMPT.md` |
| Agent transcripts with tool calls (+ error path) | Done — [`docs/demos/AGENT_TRANSCRIPTS.md`](docs/demos/AGENT_TRANSCRIPTS.md) |
| Deployed Databricks App (MCP) | Done — `mcp-weather-forecast` RUNNING |
| GitHub ↔ Databricks source sync | Done |
| Agent Bricks UI config screenshot | **Manual** — see below (SSO blocks automation) |
| Optional dashboard Databricks App | Code ready; not deployed (3-app limit) |

## Architecture

```
Agent Bricks / AI Playground / FMAPI demo agent
        |  MCP tools (same functions)
        v
mcp_server/weather_mcp_server.py   ← App: mcp-weather-forecast
        |
        v
shared/weather_broker.py  (canonical; copied into mcp_server/ + dashboard/)
        ├── Open-Meteo geocoding (TTL cache) + retries/backoff
        ├── Open-Meteo forecast/current
        └── NWS alerts (US stretch)
```

## Live deployment

| Item | Value |
|------|-------|
| Workspace | https://dbc-da72c144-83db.cloud.databricks.com/ |
| App | `mcp-weather-forecast` |
| App URL | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Workspace source | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` |

## Tools

| Tool | Capability |
|------|------------|
| `get_current_weather(location)` | Temp °F, conditions, humidity, wind |
| `get_forecast(location, days)` | Daily high/low, precip chance, conditions |
| `get_travel_recommendation(location, date)` | Derived umbrella + jacket advice |
| `compare_locations` / `get_severe_weather_alerts` | Stretch |

Prediction thresholds (env-tunable): umbrella if precip > 40%; jacket warm `<50°F` / light `<65°F`.

## Shared broker (DRY)

```bash
python scripts/sync_shared.py   # copies shared/weather_broker.py → mcp_server/ + dashboard/
```

Databricks Apps deploy per-folder, so both apps still ship a local `weather_broker.py`;
the sync script is the single source of truth to prevent drift.

## Local setup

```bash
python scripts/sync_shared.py
cd mcp_server && pip install -r requirements.txt && python test_weather.py
python weather_mcp_server.py
```

Agent transcript demos (needs workspace PAT):

```bash
export DATABRICKS_HOST=https://dbc-da72c144-83db.cloud.databricks.com
export DATABRICKS_TOKEN=<pat>
pip install openai 'databricks-sdk[openai]'
python scripts/run_agent_demos.py
```

## Register MCP in Agent Bricks (UI — for screenshot credit)

1. **AI Playground** → Tools-enabled model → **Tools → MCP Servers** →  
   `https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp`
2. **Agents → Agent Bricks → Create agent** → attach MCP tools → paste `agent/SYSTEM_PROMPT.md`
3. Screenshot config + 3 chats (Chicago / Seattle / Nowhereville) → `docs/demos/screenshots/`

Detailed click-path: see prior agent message / `docs/demos/FEEDBACK_REMEDIATION.md`.

## Sync GitHub ↔ Databricks

```bash
python scripts/sync_shared.py
databricks sync --full . /Users/sandeeptidke.work@gmail.com/weather-mcp-server
databricks apps deploy mcp-weather-forecast \
  --source-code-path /Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/mcp_server \
  --mode SNAPSHOT
```

## Demo transcripts

See [`docs/demos/AGENT_TRANSCRIPTS.md`](docs/demos/AGENT_TRANSCRIPTS.md) and [`SUBMISSION.md`](SUBMISSION.md).
