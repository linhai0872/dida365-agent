"""dida365-agent-mcp has been renamed to dida365-agent.

This package is a thin redirect: installing it pulls in `dida365-agent`,
which provides the `dida`, `dida365-agent`, `dida365-mcp`, and `dida365-oauth`
commands. Please depend on `dida365-agent` directly going forward.
"""

__all__: list[str] = []
