# CLI 命令参考

所有命令默认输出 JSON 到 stdout；出错时信息进 stderr，退出码非零。每个命令都可用 `--help` 查看完整参数。

零安装运行：`uvx dida365-agent <命令>`。本地安装后可用短命令 `dida <命令>`。

## 认证

```bash
dida auth login              # 浏览器 OAuth 授权，保存 token（约 180 天）
dida auth status             # 查看当前 token 状态
dida auth logout             # 删除本地 token
dida auth token <TOKEN>      # 直接写入 access token（跳过浏览器）
```

## 清单（Project）

```bash
dida project list                          # 列出所有清单（先调用以获取 ID）
dida project get <projectId>               # 清单详情
dida project data <projectId>              # 清单 + 其下任务 + 看板列
dida project create --name "工作" [--color --view-mode list|kanban|timeline --kind TASK|NOTE]
dida project update <projectId> [--name --color --view-mode --kind --sort-order]
dida project delete <projectId>            # 永久删除清单及其所有任务
```

## 任务（Task）

```bash
dida task create --title "标题" --project <projectId> \
  [--content --desc --start-date --due-date --priority 0|1|3|5 \
   --tags 工作,紧急 --all-day --time-zone --reminders --repeat-flag --kind --sort-order]
dida task update <taskId> --project <projectId> [同 create 的可选字段]
dida task get <projectId> <taskId>         # 按清单+任务 ID 获取
dida task get-by-id <taskId>               # 仅凭 task ID 获取
dida task complete <projectId> <taskId>    # 标记完成
dida task delete <projectId> <taskId>      # 永久删除
dida task move --task <taskId> --from <projectId> --to <projectId>

# 查询
dida task completed [--projects --start-date --end-date]
dida task filter [--projects --start-date --end-date --priority 3,5 --tags 工作 --status 0,2]
dida task undone [--projects --start-date --end-date]

# 批量（--json '<JSON数组>' 或 --file <path>）
dida task batch-create --json '[{"title":"A","projectId":"p1"}]'
dida task batch-update --json '[{"id":"t1","projectId":"p1","title":"新"}]'
dida task batch-complete --project <projectId> --tasks t1,t2,t3
```

## 全文搜索（V2）

```bash
dida search "关键词" [--projects --tags --status 0,2 --due-from <ms> --due-to <ms>]
```

## 标签（V2）

```bash
dida tag list
dida tag create --json '[{"name":"工作"}]'
dida tag update --json '[{"name":"工作","color":"#FF0000"}]'
dida tag delete-batch --json '[{"name":"旧标签"}]'
dida tag delete <name>                     # 删除单个标签
```

## 习惯（V2）

```bash
dida habit list
dida habit create --json '[{"name":"阅读"}]'
dida habit update --json '[{"id":"h1","name":"晨读"}]'
dida habit delete --json '[{"id":"h1"}]'
dida habit checkin <habitId> <YYYYMMDD> [--status 2 --value --goal]
dida habit undo-checkin <habitId> <YYYYMMDD>
dida habit checkins <habitId> [--after YYYYMMDD]
dida habit sections
```

## 父子任务与置顶（V2）

```bash
dida task set-parent <taskId> <parentId>
dida task unset-parent <taskId>
dida task pin <taskId> [--pinned/--unpinned]
```

## 项目文件夹（V2）

```bash
dida folder list
dida folder create --name "个人" [--sort-order]
dida folder update <folderId> [--name --sort-order]
dida folder delete <folderId>
```

## 约定

- **优先级**：0=无, 1=低, 3=中, 5=高
- **状态**：0=正常/未完成, 2=已完成
- **任务日期**：`yyyy-MM-dd'T'HH:mm:ssZ`，中国区用 `+0800`（如 `2026-05-29T15:00:00+0800`）
- **习惯打卡日期**：`YYYYMMDD`（如 `20260529`）
- **多值参数**用逗号分隔（`--tags 工作,紧急`、`--priority 3,5`）
- **V2 命令**需要配置 V2 认证，见 [配置说明](configuration.md)
