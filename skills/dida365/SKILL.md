---
name: dida365
description: 通过 dida CLI 管理滴答清单 / TickTick 的任务、清单、标签、习惯、文件夹。当用户要查看/创建/更新/完成/删除/搜索任务,管理清单或标签,打卡习惯,整理待办,做每日计划或复盘时使用。触发词包括 "我今天有什么任务"、"创建一个任务"、"标记完成"、"整理待办"、"本周完成了什么"、"搜索任务"、"列出标签"、"习惯打卡"、"滴答清单"、"dida"、"ticktick"。
---

# 滴答清单 / TickTick (dida CLI)

通过 `dida` 命令操作滴答清单。所有命令默认输出 JSON 到 stdout;出错时信息进 stderr 且退出码非零。
本文件只讲**何时用哪个命令、如何编排与决策**;每个命令的字面参数请用 `dida <group> <action> --help` 查看。

## 严格遵守 (NEVER DO)
- 只用 `dida` 命令操作,禁止直接 curl / HTTP API / 浏览器。
- 不要凭空编造 project_id / task_id —— 一律先用 list 命令拿到真实 ID。
- 删除类操作(`task delete` / `project delete` / `tag delete` / `folder delete`)不可撤销,执行前先向用户确认。

## 前置约定
- **先拿 ID**:任何针对具体任务/清单的操作前,先 `dida project list` 拿 project_id;清单内任务用 `dida project data <projectId>` 或 `dida task filter`。
- **任务的增删改查都需要 project_id 和 task_id**(`get-by-id` 例外,只需 task_id)。
- **日期格式**:`yyyy-MM-dd'T'HH:mm:ssZ`,中国区用 `+0800`。例:`2026-05-29T15:00:00+0800`。
- **优先级**:0=无, 1=低, 3=中, 5=高。
- **状态**:0=正常/未完成, 2=已完成。
- **习惯打卡日期**用 `YYYYMMDD`(如 `20260529`),与任务日期格式不同。

## 编排规则(多命令组合)
- **"整理 / 复盘 / 我有哪些待办"**:先 `dida task undone` 或 `dida task filter --status 0` 拉取,把结果呈现给用户确认,**再**执行后续移动/完成/删除。不要直接批量改。
- **"本周/上周完成了什么"**:用 `dida task completed --start-date ... --end-date ...`。
- **创建任务但用户没指定清单**:先 `dida project list` 列出清单让用户选;不要随意猜一个 project_id。
- **批量操作优先用 batch 命令**:要完成/创建/更新多条任务时,用 `task batch-create` / `task batch-update` / `task batch-complete`,而不是循环调用单条命令(更快、更省往返)。batch 命令通过 `--json '<JSON数组>'` 或 `--file <path>` 传入。

## filter vs search 怎么选
- **`dida task filter`**(V1):按结构化条件(清单、日期范围、优先级、标签、状态)筛选,标签是 AND 逻辑。无需 V2 配置。
- **`dida search <关键词>`**(V2):服务端全文搜索任务标题/内容。需要关键词匹配时用它,需要 V2 配置。

## V2 能力(标签 / 搜索 / 父子任务 / 习惯 / 文件夹)
这些命令需要 V2 配置(`DIDA365_V2_SESSION_TOKEN`,或 `DIDA365_USERNAME`+`DIDA365_PASSWORD`)。
若命令报 "V2 not configured",告诉用户在 `.env` 里配置其一:
- 推荐:浏览器登录 dida365.com → F12 → Application → Cookies → 复制 `t` 的值 → 设为 `DIDA365_V2_SESSION_TOKEN`(约 30 天有效)。

## 错误恢复
- **V1 401 / "Unauthorized"**:token 过期(约 180 天),运行 `dida auth login` 重新授权;查看状态用 `dida auth status`。
- **V2 401**:session token 过期(约 30 天),按上面 V2 说明更新 `DIDA365_V2_SESSION_TOKEN`。
- **404**:project_id 或 task_id 不存在,用对应 list 命令重新获取有效 ID。
- **429**:限流,等 30-60 秒再试。

## 命令速查(用 --help 看细节)
- `dida auth login | status | logout | token <TOKEN>`
- `dida project list | get | data | create | update | delete`
- `dida task create | update | get | get-by-id | complete | delete | move | completed | filter | undone | batch-create | batch-update | batch-complete | set-parent | unset-parent | pin`
- `dida search <关键词>`(V2)
- `dida tag list | create | update | delete-batch | delete`(V2)
- `dida habit list | create | update | delete | checkin | undo-checkin | checkins | sections`(V2)
- `dida folder list | create | update | delete`(V2)
