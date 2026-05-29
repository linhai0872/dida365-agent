<h1 align="center">dida365-agent</h1>

<p align="center">
  <strong>Let AI agents manage your Dida365 / TickTick — CLI · Skill · MCP</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/dida365-agent/"><img src="https://img.shields.io/pypi/v/dida365-agent" alt="PyPI"></a>
  <a href="https://pypi.org/project/dida365-agent/"><img src="https://img.shields.io/pypi/dm/dida365-agent" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white" alt="Python 3.12+">
</p>

<p align="center">
  English | <a href="README_zh.md">中文</a>
</p>

Let AI agents manage [Dida365](https://dida365.com) / [TickTick](https://ticktick.com) tasks, projects, tags, and habits through natural language. Three form factors: a lightweight **CLI**, a ready-to-install **Agent Skill**, and a standard **MCP Server**.

No install required — run it directly with `uvx`. Supports both Dida365 (China) and TickTick (International), switchable with one env var.

---

## Features

<table>
<tr><td><b>Full task management</b></td><td>Create, update, complete, delete, and move tasks with priority, tags, dates, reminders, recurrence, and checklist items — plus batch operations.</td></tr>
<tr><td><b>Projects & queries</b></td><td>CRUD projects (list / kanban / timeline views), filter by project, date, priority, tag, and status, and review completed tasks.</td></tr>
<tr><td><b>V2 advanced power</b></td><td>Server-side full-text search, tag management, habit check-ins, project folders, parent/child tasks, task pinning — capabilities the official Open API doesn't cover.</td></tr>
<tr><td><b>Three form factors</b></td><td>CLI (run-and-exit, saves resources and context), Agent Skill (one-command install with built-in methodology), MCP Server (long-running, tool calls).</td></tr>
<tr><td><b>Dual platform</b></td><td>Switch between Dida365 (China) and TickTick (International) with <code>DIDA365_REGION</code>.</td></tr>
<tr><td><b>Agent-friendly</b></td><td>Structured JSON to stdout by default, errors to stderr with non-zero exit codes — easy for agents to parse and orchestrate.</td></tr>
</table>

---

## Quick Start

### Option 1: Use the CLI directly

No install needed — run with `uvx` (requires [uv](https://docs.astral.sh/uv/getting-started/installation/)). First prepare credentials per the [configuration guide](docs/configuration.md) and write them to `.env`:

```bash
# Browser OAuth (saves token, ~180 days)
uvx dida365-agent dida auth login

# List all projects
uvx dida365-agent dida project list

# Create a high-priority task due tomorrow
uvx dida365-agent dida task create --title "Review PR" --project <projectId> \
  --priority 5 --due-date "2026-05-30T18:00:00+0800"

# Full-text search (V2)
uvx dida365-agent dida search "meeting"
```

> After installing locally (`uv tool install dida365-agent`), use the shorter `dida` command.

### Option 2: Use as an Agent Skill

Install the Skill in any Skill-compatible AI tool (Claude Code, Cursor, etc.) and drive it with natural language:

```bash
# Install the Skill
npx skills add linhai0872/dida365-agent
```

Then just describe what you need in the AI chat:

> Tidy up my unfinished tasks for today, list the high-priority ones, and move the overdue ones to the "Later" project

The Skill recognizes intent, fills in missing details, and assembles `dida` commands automatically — no manual parameters required.

### Option 3: As an MCP Server

Exposes 44 tools as a standard MCP Server for Claude Code, Cursor, Windsurf, etc. See [MCP Server integration](docs/mcp.md).

---

## Documentation

| Doc | Contents |
|-----|----------|
| [CLI Reference](docs/cli.md) | All commands, parameters, conventions |
| [Configuration](docs/configuration.md) | Credentials, enabling V2, env vars, token lifecycle |
| [MCP Server](docs/mcp.md) | Local / source / Docker deployment, AI tool config |

---

## Development

```bash
uv sync                              # Install dependencies
uv run python -m pytest tests/       # Run tests
uv run ruff check src/ tests/        # Lint
uv run dida --help                   # Run the CLI locally
```

## License

[MIT](LICENSE)

## Acknowledgments

- [Dida365](https://developer.dida365.com/docs#/openapi) / [TickTick](https://developer.ticktick.com/docs#/openapi) Open API
- [FastMCP](https://github.com/jlowin/fastmcp) · [Typer](https://typer.tiangolo.com/) · [Model Context Protocol](https://modelcontextprotocol.io/)
