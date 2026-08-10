# Feedback remediation notes

Addressed reviewer feedback in this pass:

| Feedback | Remediation |
|----------|-------------|
| Register MCP in Agent Bricks + chat transcripts with tool calls | Live tool-calling transcripts in `docs/demos/AGENT_TRANSCRIPTS.md` (Databricks Llama 3.3 70B + same MCP tool functions + `SYSTEM_PROMPT.md`). **Agent Bricks UI screenshots still need to be captured in-workspace** (Google SSO blocks automation). |
| Error-path transcript (`Nowhereville, Atlantis`) | Included as transcript #3 — tool returns `status=error`, assistant asks for clarification. |
| Retries/backoff around HTTP | `shared/weather_broker.py` uses urllib3 `Retry` + exponential backoff for 429/5xx and transport errors. |
| Geocode caching | In-process TTL cache (`GEOCODE_CACHE_TTL_SEC`, default 1h). |
| DRY dashboard broker copy | Canonical module is `shared/weather_broker.py`; `scripts/sync_shared.py` copies it into `mcp_server/` and `dashboard/` before deploy. |

## How to capture Agent Bricks UI evidence (required for full credit)

1. Open https://dbc-da72c144-83db.cloud.databricks.com/
2. **AI Playground** → Tools-enabled model → **Tools → MCP Servers** → add  
   `https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp`
3. **Agents → Agent Bricks → Create agent** → attach MCP tools → paste `agent/SYSTEM_PROMPT.md`
4. Screenshot: Agent Bricks config page showing MCP attached
5. Screenshot/chat: Chicago, Seattle jacket/umbrella, Nowhereville error clarification
6. Drop screenshots into `docs/demos/screenshots/` and link them from `SUBMISSION.md`
