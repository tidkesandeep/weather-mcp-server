# Submission — Weather-Prediction MCP Server + Agent

**Student:** Sandeep Tidke  
**Repo:** https://github.com/tidkesandeep/weather-mcp-server  
**Branches:** `main`, `develop` (identical at `f53af28`+; see latest commit)  
**Date:** 2026-08-10  
**Workspace:** https://dbc-da72c144-83db.cloud.databricks.com/

## Requirements checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | FastMCP MCP server, streamable HTTP, `@mcp.tool` | **Done** — `mcp_server/weather_mcp_server.py` |
| 2 | Separate broker/adapter (all HTTP/parsing) | **Done** — `mcp_server/weather_broker.py` |
| 3 | Current conditions tool | **Done** — `get_current_weather` |
| 4 | Multi-day forecast tool | **Done** — `get_forecast` |
| 5 | Prediction/recommendation with threshold logic | **Done** — `get_travel_recommendation` |
| 6 | Docstrings (Args/Returns) + clean errors | **Done** |
| 7 | `requirements.txt` + `app.yaml` for MCP app | **Done** |
| 8 | Free weather API; no secrets in git | **Done** — Open-Meteo (none) + NWS stretch |
| 9 | Agent system prompt + tool order/guardrails | **Done** — `agent/SYSTEM_PROMPT.md` |
| 10 | README (architecture, tools, setup, API/auth) | **Done** |
| 11 | ≥3 NL demos with tool calls + answers | **Done** (below) |
| 12 | MCP deployed as Databricks App | **Done** — `mcp-weather-forecast` RUNNING |
| 13 | GitHub code ↔ Databricks app source in sync | **Done** — verified byte-identical |
| 14 | Register MCP + Agent Bricks Custom LLM | **Remaining UI step** (cannot create via API) |
| 15 | Optional dashboard app | **Code done**; not deployed (3-app workspace limit) |

### Stretch extras included

- `compare_locations` — multi-city forecast compare  
- `get_severe_weather_alerts` — US NWS alerts  
- `dashboard/` Flask UI ready to deploy when a slot frees up  

## Databricks deployment

| Item | Value |
|------|-------|
| App | `mcp-weather-forecast` |
| App URL | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Health | `/healthz` → 200 |
| Workspace sync path | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` |
| App source path | `.../weather-mcp-server/mcp_server` |
| Git folder | `.../weather-mcp-server-repo` tracking GitHub **`develop`** |

### Remaining UI action (Agent Bricks)

1. **AI Playground** → tools-enabled model → **Tools → MCP Servers** → add  
   `https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp`
2. **Agents → Agent Bricks → Create agent** (Custom LLM).
3. Attach the MCP tools; paste [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md).
4. Re-run the three demos below and capture screenshots for the write-up.

## Weather API + auth

**Open-Meteo** (primary) — no signup, no API key.  
**NWS alerts** (stretch) — no API key; US-only.

## Demo transcripts (live tool-equivalent calls)

Captured 2026-08-10 by calling the same broker functions the `@mcp.tool` wrappers use.
Raw JSON also in [`docs/demos/tool_outputs.json`](docs/demos/tool_outputs.json).

### 1. "What's the weather in Chicago right now?"

**Tool:** `get_current_weather("Chicago")`

```json
{
  "location": "Chicago, Illinois, US",
  "temperature_f": 80.9,
  "conditions": "Mainly clear",
  "humidity_pct": 93,
  "wind_mph": 2.7,
  "precipitation_mm": 0.0,
  "as_of": "2026-08-10T13:30"
}
```

**Answer:** Mainly clear in Chicago — about **80.9°F**, humidity **93%**, wind **2.7 mph** (as of 2026-08-10T13:30 local).

### 2. "Will it rain in Austin this weekend?"

**Tool:** `get_forecast("Austin, TX", days=7)`

Weekend (Sat–Sun 2026-08-15 / 2026-08-16):

| Date | High | Low | Precip | Conditions |
|------|------|-----|--------|------------|
| 2026-08-15 | 104.4°F | 79.3°F | 2% | Overcast |
| 2026-08-16 | 105.6°F | 79.2°F | 1% | Mainly clear |

**Answer:** Rain looks unlikely — precip ~1–2%. Hot and mostly dry, highs around 104–106°F.

### 3. "Should I bring a jacket and umbrella to Seattle tomorrow?"

**Tool:** `get_travel_recommendation("Seattle", "tomorrow")`

```json
{
  "date": "2026-08-11",
  "high_f": 76.6,
  "low_f": 55.9,
  "precip_chance_pct": 3,
  "conditions": "Clear sky",
  "umbrella_needed": false,
  "jacket": "light",
  "recommendation": "Skip the umbrella; jacket=light.",
  "reasoning": "On 2026-08-11 in Seattle, Washington, US: high 76.6°F / low 55.9°F, Clear sky, 3% chance of precipitation. Umbrella not required (precip 3% ≤ 40% threshold). A light jacket is recommended (overnight low 55.9°F < 65°F)."
}
```

**Answer:** Skip the umbrella (3% < 40% threshold). Bring a **light jacket** (overnight low ~56°F).

### 4. Error handling — "What's the weather in Nowhereville, Atlantis?"

```json
{
  "status": "error",
  "message": "Could not resolve location 'Nowhereville, Atlantis'. Try a clearer city name (e.g. 'Chicago, IL') or 'lat,lon'."
}
```

**Answer:** Location could not be resolved — please clarify the city or coordinates.

### 5. Stretch — "Any severe weather alerts for Miami?"

**Tool:** `get_severe_weather_alerts("Miami, FL")` → active **Heat Advisory** (NWS Miami).

## Agent system prompt

Full text: [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md)

- Never invent weather — always call a tool first  
- On `status=error`, ask the user to clarify  
- Explain recommendation thresholds  
- NWS alerts are US-only  

## Sync verification (last checked)

| Surface | Result |
|---------|--------|
| `origin/main` == `origin/develop` | Same commit |
| Local `mcp_server/*` vs Workspace path | SHA256 match |
| Local `mcp_server/*` vs App deployment artifact | SHA256 match |
| Git folder `weather-mcp-server-repo` | On `develop`, same commit as GitHub |
| App status | RUNNING / deploy SUCCEEDED |
| Broker smoke tests | 5/5 passed |

## Branching

- `main` — stable submission  
- `develop` — development mirror (kept identical for this submission)  
- Commits authored as **Sandeep Tidke** `<tidke.sandeep4@gmail.com>`
