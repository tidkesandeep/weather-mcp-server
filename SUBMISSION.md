# Submission — Weather-Prediction MCP Server + Agent

**Student:** Sandeep Tidke  
**Repo:** https://github.com/tidkesandeep/weather-mcp-server  
**Branches:** `main`, `develop`  
**Date:** 2026-08-10  
**Workspace:** https://dbc-da72c144-83db.cloud.databricks.com/

## Requirements checklist

| # | Requirement | Status |
|---|-------------|--------|
| 1 | FastMCP MCP server, streamable HTTP | **Done** |
| 2 | Separate broker/adapter | **Done** — `shared/weather_broker.py` (+ sync into apps) |
| 3–5 | Current / forecast / recommendation tools | **Done** (+ stretch compare + NWS alerts) |
| 6 | Docstrings + clean errors | **Done** |
| 7 | `requirements.txt` + `app.yaml` | **Done** |
| 8 | Free API; no secrets in git | **Done** (Open-Meteo + NWS) |
| 9 | Agent system prompt | **Done** — `agent/SYSTEM_PROMPT.md` |
| 10 | README | **Done** |
| 11 | ≥3 NL demos with tool calls + answers | **Done** — see transcripts below |
| 12 | MCP Databricks App deployed | **Done** — `mcp-weather-forecast` RUNNING |
| 13 | GitHub ↔ app source sync | **Done** |
| 14 | Agent Bricks UI config screenshot | **Manual follow-up** (SSO blocks automation) |
| 15 | Optional dashboard app | Code ready; not deployed (3-app limit) |

### Feedback remediation

| Feedback item | Status |
|---------------|--------|
| Agent chat transcripts with tool calls | **Done** — [`docs/demos/AGENT_TRANSCRIPTS.md`](docs/demos/AGENT_TRANSCRIPTS.md) |
| Error-path transcript (`Nowhereville, Atlantis`) | **Done** — transcript #3 asks for clarification |
| HTTP retries/backoff | **Done** — urllib3 Retry + exponential backoff |
| Geocode caching | **Done** — in-process TTL cache |
| DRY `weather_broker.py` | **Done** — `shared/` + `scripts/sync_shared.py` |
| Agent Bricks config screenshot | **Needs your UI login** — steps in `docs/demos/FEEDBACK_REMEDIATION.md` |

## Databricks deployment

| Item | Value |
|------|-------|
| App | `mcp-weather-forecast` |
| App URL | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com |
| MCP endpoint | https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp |
| Workspace source | `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/mcp_server` |

## Agent transcripts (prompt adherence)

Generated with Databricks Model Serving (`databricks-meta-llama-3-3-70b-instruct`) using
`agent/SYSTEM_PROMPT.md` and the **same tool functions** as the deployed MCP server
(`scripts/run_agent_demos.py`). Full write-up: [`docs/demos/AGENT_TRANSCRIPTS.md`](docs/demos/AGENT_TRANSCRIPTS.md).

### 1. "What's the weather in Chicago right now?"

- **Tool:** `get_current_weather({"location":"Chicago, IL"})` → mainly clear, 80.9°F, 93% humidity, 2.7 mph
- **Final:** Reports those values only (no invented data)

### 2. "Should I bring a jacket and umbrella to Seattle tomorrow?"

- **Tool:** `get_travel_recommendation({"location":"Seattle","date":"tomorrow"})` → precip 3%, jacket=light
- **Final:** Skip umbrella (3% < 40% threshold); bring a light jacket (low 55.9°F < 65°F)

### 3. Error path — "What's the weather in Nowhereville, Atlantis?"

- **Tool:** `get_current_weather(...)` → `{"status":"error","message":"Could not resolve location..."}`
- **Final:** Does **not** invent weather; asks for a clearer city name or `lat,lon` (guardrail hit)

## Capture Agent Bricks UI evidence (for full credit)

1. Log into the workspace (Google SSO).
2. Playground → add MCP URL above → confirm tools list.
3. Agent Bricks → Custom LLM → attach MCP → paste `agent/SYSTEM_PROMPT.md`.
4. Screenshot: config with MCP attached.
5. Re-run the 3 chats above; screenshot tool calls + answers.
6. Save under `docs/demos/screenshots/` and link here.

## Weather API + auth

Open-Meteo (primary, no key) + NWS alerts stretch (no key, US-only).

## Robustness notes

- HTTP: session-level retries for 429/5xx + transport errors with exponential backoff
- Geocode: TTL cache (default 3600s) to reduce repeated lookups
- DRY: edit `shared/weather_broker.py`, then `python scripts/sync_shared.py`

## Branching / authorship

Commits authored as **Sandeep Tidke** `<tidke.sandeep4@gmail.com>` on `main` and `develop`.
