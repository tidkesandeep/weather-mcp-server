# Submission — Weather-Prediction MCP Server + Agent

**Student:** Sandeep Tidke  
**Repo:** https://github.com/tidkesandeep/weather-mcp-server  
**Branches:** `main`, `develop`  
**Date:** 2026-08-10  
**Workspace:** https://dbc-da72c144-83db.cloud.databricks.com/

## Checklist

| Requirement | Status |
|-------------|--------|
| FastMCP server with streamable HTTP (`mcp_server/weather_mcp_server.py`) | Done |
| Adapter module with all HTTP/parsing (`weather_broker.py`) | Done |
| ≥3 tools: current, forecast, prediction/recommendation | Done (+2 stretch) |
| `app.yaml` + `requirements.txt` for MCP Databricks App | Done |
| Agent system prompt + tool list (`agent/`) | Done |
| README with architecture, tools, setup, API/auth | Done |
| No secrets / no hardcoded API keys | Done (Open-Meteo + NWS are keyless) |
| Error handling returns clean `status=error` dicts | Done |
| Optional dashboard app (`dashboard/`) | Done (stretch) |
| ≥3 NL demo Q&A with tool calls + answers | Done (below) |

## Databricks App URLs

| App | URL / notes |
|-----|-------------|
| MCP server (`mcp-weather-forecast`) | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Workspace source (synced) | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` |
| Dashboard (optional stretch) | Code in `dashboard/`; deploy when an app slot is free |

> **Register in workspace UI (Agent Bricks / AI Playground):**
> 1. Open **AI Playground**, pick a **Tools enabled** model.
> 2. **Tools → Add tool → MCP Servers** → add
>    `https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp`
>    (streamable HTTP). Or **AI Gateway → MCPs → Register** if using Unity Catalog MCP Services.
> 3. **Agents → Agent Bricks → Create agent** (Custom LLM), attach the MCP tools, paste
>    [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md).
> 4. Re-run the three demo questions below and capture screenshots for your write-up.

## Weather API

**Open-Meteo** (primary) — no signup, no API key.  
**NWS alerts** (stretch) — no API key; US-only.

## Demo transcripts (live broker / tool-equivalent calls)

Captured 2026-08-10 by exercising the same functions the `@mcp.tool` wrappers call.

### 1. "What's the weather in Chicago right now?"

**Tool:** `get_current_weather("Chicago")`

```json
{
  "location": "Chicago, Illinois, US",
  "temperature_f": 80.5,
  "conditions": "Partly cloudy",
  "humidity_pct": 92,
  "wind_mph": 3.5,
  "precipitation_mm": 0.0,
  "as_of": "2026-08-10T13:15"
}
```

**Agent-style answer:** It's partly cloudy in Chicago right now — about **80.5°F**, humidity **92%**, wind around **3.5 mph** (as of 2026-08-10T13:15 local).

### 2. "Will it rain in Austin this weekend?"

**Tool:** `get_forecast("Austin, TX", days=7)`

Weekend (Sat–Sun 2026-08-15 / 2026-08-16):

| Date | High | Low | Precip | Conditions |
|------|------|-----|--------|------------|
| 2026-08-15 | 103.3°F | 79.3°F | 2% | Overcast |
| 2026-08-16 | 105.3°F | 78.0°F | 1% | Mainly clear |

**Agent-style answer:** Rain looks unlikely in Austin this weekend — precip chances are only ~1–2%. Expect hot, mostly dry conditions with highs around 103–105°F.

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

**Agent-style answer:** Skip the umbrella (only 3% precip chance, below the 40% threshold). Bring a **light jacket** — overnight low is about 56°F.

### 4. Error handling — "What's the weather in Nowhereville, Atlantis?"

**Tool:** `get_current_weather` → clean error

```json
{
  "status": "error",
  "message": "Could not resolve location 'Nowhereville, Atlantis'. Try a clearer city name (e.g. 'Chicago, IL') or 'lat,lon'."
}
```

**Agent-style answer:** I couldn't resolve that location — please provide a real city name or coordinates.

### 5. Stretch — "Any severe weather alerts for Miami?"

**Tool:** `get_severe_weather_alerts("Miami, FL")` → active **Heat Advisory** (NWS Miami).

## Agent system prompt (summary)

Full text: [`agent/SYSTEM_PROMPT.md`](agent/SYSTEM_PROMPT.md)

Guardrails: never invent weather; always call a tool first; on `status=error` ask the user to clarify; explain recommendation thresholds; US-only for NWS alerts.

## Sync note

GitHub `main` / `develop` and the Databricks App source path under
`/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` are kept in sync via
`databricks sync` + `databricks apps deploy`.

## Branching

- `main` — stable submission snapshot
- `develop` — development mirror (same code at submission time)
- `cursor/weather-mcp-server-0173` — feature branch used for PR review

GitHub and Databricks workspace path
`/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/` are kept in sync
via `databricks sync` + `databricks apps deploy`.
