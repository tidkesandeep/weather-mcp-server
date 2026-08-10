# Agent Bricks configuration notes

## Tools to attach

Register the deployed MCP app (streamable HTTP), then attach:

| Tool | Required |
|------|----------|
| `get_current_weather` | yes |
| `get_forecast` | yes |
| `get_travel_recommendation` | yes |
| `compare_locations` | optional (stretch) |
| `get_severe_weather_alerts` | optional (stretch) |

## Live deployment (this workspace)

- App: `mcp-weather-forecast` (**RUNNING**)
- URL: https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com
- MCP endpoint: https://mcp-weather-forecast-7474653382320337.aws.databricksapps.com/mcp
- Workspace source: `/Workspace/Users/sandeeptidke.work@gmail.com/weather-mcp-server/mcp_server`

## Registration steps (workspace UI — remaining human step)

1. **AI Playground** → pick a model labeled **Tools enabled**.
2. **Tools → + Add tool → MCP Servers** → paste the MCP endpoint above (streamable HTTP).
3. **Agents → Agent Bricks → Create agent** → Custom LLM.
4. Under **Tools**, add the MCP server (all required tools above).
5. Paste [`SYSTEM_PROMPT.md`](SYSTEM_PROMPT.md) into the system prompt.
6. Evaluate with the sample prompts below, then deploy / chat.

## Suggested sample evaluation prompts

1. What's the weather in Chicago right now?
2. Will it rain in Austin this weekend?
3. Should I bring a jacket and umbrella to Seattle tomorrow?
4. Compare the next 3 days in Chicago vs Denver.
5. Are there any severe weather alerts for Miami?
