# Agent Bricks configuration notes

## Tools to attach
Register the deployed MCP app as an external MCP (streamable HTTP), then attach:

| Tool | Required |
|------|----------|
| `get_current_weather` | yes |
| `get_forecast` | yes |
| `get_travel_recommendation` | yes |
| `compare_locations` | optional (stretch) |
| `get_severe_weather_alerts` | optional (stretch) |

## Suggested sample evaluation prompts
1. What's the weather in Chicago right now?
2. Will it rain in Austin this weekend?
3. Should I bring a jacket and umbrella to Seattle tomorrow?
4. Compare the next 3 days in Chicago vs Denver.
5. Are there any severe weather alerts for Miami?

## Registration steps (workspace UI)
1. Deploy `mcp_server/` as a Databricks App (name recommended: `mcp-weather-forecast`).
2. Copy the app URL (MCP endpoint is typically `https://<app-url>/mcp`).
3. **AI Gateway → MCPs → Add MCP** (external, streamable HTTP).
4. **Agents → Agent Bricks → Create agent** (Custom LLM).
5. Add the MCP under Tools; paste `SYSTEM_PROMPT.md` into the system prompt.
6. Evaluate with the sample prompts above, then deploy.
