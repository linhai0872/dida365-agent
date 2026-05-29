# dida365-agent-mcp → dida365-agent

This package has been **renamed to [`dida365-agent`](https://pypi.org/project/dida365-agent/)**.

`dida365-agent-mcp` is now a thin redirect that installs `dida365-agent`. Please switch your dependency:

```bash
pip install dida365-agent
```

The new package provides everything the old one did, plus a CLI and an Agent Skill:

- `dida` / `dida365-agent` — CLI (JSON output, run-and-exit)
- `dida365-mcp` — MCP server (stdio / streamable-http)
- `dida365-oauth` — OAuth helper

See the [project README](https://github.com/linhai0872/dida365-agent) for details.
