# MCP Server 集成

除了 CLI 和 Skill，本项目同时是一个标准 MCP Server，可供 Claude Code、Cursor、Windsurf 等通过工具调用直接管理任务。共 40 个工具（19 个 V1 + 21 个 V2）。

先按 [配置说明](configuration.md) 准备好凭据并完成 OAuth 授权（`uvx dida365-agent dida auth login`）。

## 本地（stdio）

<details>
<summary>Claude Code</summary>

编辑 `~/.claude/mcp.json`：

```json
{
  "mcpServers": {
    "dida365": {
      "command": "uvx",
      "args": ["--from", "dida365-agent", "dida365-mcp"]
    }
  }
}
```

</details>

<details>
<summary>Cursor</summary>

进入 **Settings > MCP > Add new global MCP server**：

```json
{
  "mcpServers": {
    "dida365": {
      "command": "uvx",
      "args": ["--from", "dida365-agent", "dida365-mcp"]
    }
  }
}
```

</details>

## 源码运行

```bash
git clone https://github.com/linhai0872/dida365-agent.git
cd dida365-agent
uv sync
cp .env.example .env   # 填入 CLIENT_ID 和 CLIENT_SECRET
uv run dida365-oauth   # OAuth 授权
uv run dida365-mcp     # 启动（stdio）
```

MCP 客户端配置：

```json
{
  "mcpServers": {
    "dida365": {
      "command": "uv",
      "args": ["--directory", "/path/to/dida365-agent", "run", "dida365-mcp"]
    }
  }
}
```

## 远程（Docker + HTTP）

适用于持续运行或团队共享。

```bash
git clone https://github.com/linhai0872/dida365-agent.git
cd dida365-agent
cp .env.example .env
# 在 .env 中填入 DIDA365_REGION 和 DIDA365_ACCESS_TOKEN
docker compose up -d
```

连接地址：`http://your-host:8000/mcp`

> 容器内无法打开浏览器，需在 `.env` 中直接设置 `DIDA365_ACCESS_TOKEN`（先在本地完成 OAuth 获取）。

## 工具一览

工具按能力与 CLI 命令一一对应（如 `dida365_create_task` ↔ `dida task create`）。V1 工具始终可用，V2 工具需配置 V2 认证。

完整能力清单见 [CLI 命令参考](cli.md)——两者覆盖相同的操作集。
