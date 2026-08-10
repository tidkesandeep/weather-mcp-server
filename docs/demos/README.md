# Demo artifacts

| File | Contents |
|------|----------|
| [`AGENT_TRANSCRIPTS.md`](AGENT_TRANSCRIPTS.md) | Human-readable agent chats with tool calls + final answers (incl. error path) |
| [`agent_transcripts.json`](agent_transcripts.json) | Machine-readable version of the same |
| [`tool_outputs.json`](tool_outputs.json) | Raw broker/tool outputs |
| [`FEEDBACK_REMEDIATION.md`](FEEDBACK_REMEDIATION.md) | How feedback items were addressed |
| `screenshots/` | Drop Agent Bricks / Playground UI screenshots here after manual capture |

Regenerate transcripts:

```bash
export DATABRICKS_HOST=https://dbc-da72c144-83db.cloud.databricks.com
export DATABRICKS_TOKEN=<pat>
python scripts/run_agent_demos.py
```
