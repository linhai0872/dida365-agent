<h1 align="center">dida365-agent</h1>

<p align="center">
  <strong>让 AI Agent 管理你的滴答清单 / TickTick — CLI · Skill · MCP</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/dida365-agent/"><img src="https://img.shields.io/pypi/v/dida365-agent" alt="PyPI"></a>
  <a href="https://pypi.org/project/dida365-agent/"><img src="https://img.shields.io/pypi/dm/dida365-agent" alt="Downloads"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
  <img src="https://img.shields.io/badge/python-3.12+-blue?logo=python&logoColor=white" alt="Python 3.12+">
</p>

<p align="center">
  <a href="README.md">English</a> | 中文
</p>

让 AI Agent 用自然语言管理[滴答清单](https://dida365.com) / [TickTick](https://ticktick.com) 的任务、清单、标签、习惯。提供三种形态：轻量 **CLI**、即装即用的 **Agent Skill**、标准 **MCP Server**。

无需安装，通过 `uvx` 命令即可直接使用。同时支持滴答清单（国内）和 TickTick（国际），一个环境变量切换。

---

## 功能特性

<table>
<tr><td><b>任务全管理</b></td><td>创建、更新、完成、删除、移动任务，支持优先级、标签、日期、提醒、重复规则、子任务（清单项），并提供批量操作。</td></tr>
<tr><td><b>清单与查询</b></td><td>清单（列表 / 看板 / 时间线视图）增删改查，按项目、日期、优先级、标签、状态多维筛选，回顾已完成任务。</td></tr>
<tr><td><b>V2 进阶能力</b></td><td>服务端全文搜索、标签管理、习惯打卡、项目文件夹、父子任务、任务置顶 —— 官方 Open API 未覆盖的能力。</td></tr>
<tr><td><b>三种形态</b></td><td>CLI（用完即走，省资源省 context）、Agent Skill（一键安装，内置使用方法论）、MCP Server（常驻服务，工具调用）。</td></tr>
<tr><td><b>双平台</b></td><td>通过 <code>DIDA365_REGION</code> 在滴答清单（国内）与 TickTick（国际）间一键切换。</td></tr>
<tr><td><b>Agent 友好</b></td><td>默认输出结构化 JSON，错误进 stderr + 非零退出码，便于 Agent 解析与编排。</td></tr>
</table>

---

## 快速上手

### 方式一：命令行直接使用

无需安装，通过 `uvx` 即可直接运行（需 [uv](https://docs.astral.sh/uv/getting-started/installation/)）。先按 [配置说明](docs/configuration.md) 准备凭据，写入 `.env`：

```bash
# 浏览器 OAuth 授权（保存 token，约 180 天）
uvx dida365-agent dida auth login

# 列出所有清单
uvx dida365-agent dida project list

# 创建一个高优先级任务，截止明天
uvx dida365-agent dida task create --title "评审 PR" --project <projectId> \
  --priority 5 --due-date "2026-05-30T18:00:00+0800"

# 全文搜索（V2）
uvx dida365-agent dida search "会议"
```

> 安装到本地后（`uv tool install dida365-agent`），可用更短的 `dida` 命令。

### 方式二：通过 Agent Skill 使用

在支持 Skill 协议的 AI 工具（Claude Code、Cursor 等）中安装 Skill，用自然语言驱动操作：

```bash
# 安装 Skill
npx skills add linhai0872/dida365-agent
```

安装后，直接在 AI 对话中描述需求：

> 帮我把今天没完成的任务整理一下，高优先级的列出来，过期的移到「稍后处理」清单

Skill 会识别意图、补全缺失信息、自动组装 `dida` 命令执行，全程无需手动输入参数。

### 方式三：作为 MCP Server

作为标准 MCP Server 暴露 44 个工具，供 Claude Code、Cursor、Windsurf 等直连。详见 [MCP Server 集成](docs/mcp.md)。

---

## 文档

| 文档 | 内容 |
|------|------|
| [CLI 命令参考](docs/cli.md) | 全部命令、参数、约定 |
| [配置说明](docs/configuration.md) | 凭据获取、V2 启用、环境变量、Token 生命周期 |
| [MCP Server 集成](docs/mcp.md) | 本地 / 源码 / Docker 部署，AI 工具直连配置 |

---

## 开发

```bash
uv sync                              # 安装依赖
uv run python -m pytest tests/       # 运行测试
uv run ruff check src/ tests/        # 代码检查
uv run dida --help                   # 本地运行 CLI
```

## 许可证

[MIT](LICENSE)

## 致谢

- [滴答清单](https://developer.dida365.com/docs#/openapi) / [TickTick](https://developer.ticktick.com/docs#/openapi) Open API
- [FastMCP](https://github.com/jlowin/fastmcp) · [Typer](https://typer.tiangolo.com/) · [Model Context Protocol](https://modelcontextprotocol.io/)
