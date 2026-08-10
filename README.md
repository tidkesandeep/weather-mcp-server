# Weather-Prediction MCP Server + Agent

Day 3 homework: build a weather-forecast MCP server (FastMCP) and wire a
Databricks Agent Bricks agent to answer natural-language weather questions.
Patterned after Day 3's `mcp_server/` + `dashboard/` Alpaca split
([databricks-lakebase-app-day-3](https://github.com/EcZachly/databricks-lakebase-app-day-3))
— reference pattern, not a verbatim copy.

**Author:** Sandeep Tidke

## Architecture

```
Agent Bricks agent  --(MCP / streamable HTTP)-->  mcp_server/weather_mcp_server.py
                                                          |
                                                          v
                                                   weather_broker.py
                                                          |
                          +---------------+---------------+----------------+
                          |               |                                |
                          v               v                                v
                     Open-Meteo      Open-Meteo                      NWS alerts
                     geocoding       forecast/current                (US stretch)
                          ^
                          |
                 dashboard/app.py  (optional human UI; own broker copy)
```

- `mcp_server/` and `dashboard/` are **two separate Databricks Apps**.
- Tool functions stay thin; all HTTP/parsing lives in `weather_broker.py`.
- **No API keys / no Databricks secrets** — Open-Meteo is keyless.

## Weather API + auth

| API | Purpose | Auth |
|-----|---------|------|
| [Open-Meteo](https://open-meteo.com/) forecast + geocoding | Current conditions + multi-day forecast | None |
| [NWS](https://www.weather.gov/documentation/services-web-api) alerts | US severe-weather alerts (stretch) | None (User-Agent only) |

## Tools

| Tool | Capability |
|------|------------|
| `get_current_weather(location)` | Temp °F, conditions, humidity, wind |
| `get_forecast(location, days)` | Daily high/low, precip chance, conditions (1–16 days) |
| `get_travel_recommendation(location, date)` | **Derived** umbrella + jacket advice (not a passthrough) |
| `compare_locations(locations, days)` | Stretch — side-by-side forecasts |
| `get_severe_weather_alerts(location)` | Stretch — US NWS active alerts |

### Prediction logic (`get_travel_recommendation`)

- **Umbrella** if `precip_chance_pct > 40`
- **Jacket** = `warm` if `low_f < 50`, `light` if `low_f < 65`, else `none`
- Returns boolean/flags plus a human-readable `reasoning` string

Bad locations and API failures return `{"status":"error","message":...}` — no stack traces to the agent.

## Repository layout

```
mcp_server/
  weather_mcp_server.py   # FastMCP entrypoint (@mcp.tool)
  weather_broker.py       # Open-Meteo / NWS adapter
  test_weather.py         # local smoke tests
  app.yaml                # Databricks App config
  requirements.txt
dashboard/                # optional stretch UI
  app.py
  weather_broker.py       # duplicated (Apps deploy per-folder)
  templates/index.html
  app.yaml
  requirements.txt
agent/
  SYSTEM_PROMPT.md        # Agent Bricks system prompt
  AGENT_CONFIG.md         # registration + eval prompts
SUBMISSION.md             # demos, URLs, checklist
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

## Deploy to Databricks Apps

1. Push this repo; create a **Git folder** in the workspace pointed at it.
2. **Compute → Apps → Create app → Custom**
   - Name: `mcp-weather-forecast` (`mcp-` prefix helps Playground discovery)
   - Source: Git folder → `mcp_server/`
   - Deploy and copy the app URL (MCP endpoint: `https://<app-url>/mcp`)
3. (Optional) Create a second app for `dashboard/`.
4. Keep GitHub and the Databricks app source path in sync (redeploy after pushes).

### CLI sync / deploy (when CLI auth is configured)

```bash
export DATABRICKS_HOST=https://<workspace>.cloud.databricks.com
export DATABRICKS_TOKEN=<pat>

databricks workspace mkdirs /Users/<you>/weather-mcp-server
databricks sync ./mcp_server /Users/<you>/weather-mcp-server/mcp_server
databricks apps create mcp-weather-forecast --description "Weather forecast MCP (Open-Meteo)"
# or update default_source_code_path, then:
databricks apps deploy mcp-weather-forecast --source-code-path /Workspace/Users/<you>/weather-mcp-server/mcp_server
```

## Register MCP + build Agent Bricks agent

1. **AI Gateway → MCPs → Add MCP** — external streamable HTTP → paste app `/mcp` URL.
2. **Agents → Agent Bricks → Create agent** (Custom LLM).
3. Attach the MCP tools listed above.
4. Paste [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md) as the system prompt.
5. Evaluate with the prompts in [`agent/AGENT_CONFIG.md`](agent/AGENT_CONFIG.md).

## Deployed app (this workspace)

| Item | Value |
|------|-------|
| App name | `mcp-weather-forecast` |
| App URL | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Workspace sync path | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` |

## Demo questions

1. What's the weather in Chicago right now?
2. Will it rain in Austin this weekend?
3. Should I bring a jacket and umbrella to Seattle tomorrow?

Live tool outputs and answers are recorded in [`SUBMISSION.md`](SUBMISSION.md).

## Branches

- `main` — submission / stable
- `develop` — active development mirror

## License / data use

Open-Meteo non-commercial free tier (~10k calls/day). NWS data is public domain.

## PR / review branch

Feature work for review also lands on `cursor/weather-mcp-server-0173` before merging to `main` / `develop`.
