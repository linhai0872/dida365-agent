# 配置说明

## 获取开发者凭据

前往开发者中心创建应用，复制 Client ID 和 Client Secret：

- 滴答清单（国内）：https://developer.dida365.com/manage
- TickTick（国际）：https://developer.ticktick.com/manage

将 **Redirect URI** 设置为 `http://localhost:8000/oauth/callback`。

## .env 配置

在项目目录（或运行命令的目录）创建 `.env`：

```env
DIDA365_REGION=china
DIDA365_CLIENT_ID=your_client_id
DIDA365_CLIENT_SECRET=your_client_secret
```

## 启用 V2 功能（标签、搜索、习惯、文件夹、父子任务）

V2 功能依赖私有 API，需要额外配置以下任一方式：

```env
# 方式 1：Session Token（手动，最安全，约 30 天有效）
# 浏览器登录 dida365.com → F12 → Application → Cookies → 复制 't' 的值
DIDA365_V2_SESSION_TOKEN=your_token

# 方式 2：自动登录（方便，不支持 2FA 账号）
DIDA365_USERNAME=your_email
DIDA365_PASSWORD=your_password
```

不配 V2 仍可使用全部 V1 功能（任务、清单、批量操作）。

## 全部配置项

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DIDA365_REGION` | `china`（dida365.com）或 `international`（ticktick.com） | `china` |
| `DIDA365_CLIENT_ID` | OAuth Client ID | — |
| `DIDA365_CLIENT_SECRET` | OAuth Client Secret | — |
| `DIDA365_ACCESS_TOKEN` | Access Token（直接设置可跳过 OAuth） | — |
| `DIDA365_REDIRECT_URI` | OAuth 回调地址 | `http://localhost:8000/oauth/callback` |
| `DIDA365_V2_SESSION_TOKEN` | V2 Session Token（浏览器 cookie `t`，约 30 天有效） | — |
| `DIDA365_USERNAME` | V2 自动登录邮箱/手机（与 session token 二选一） | — |
| `DIDA365_PASSWORD` | V2 自动登录密码（不支持 2FA 账号） | — |
| `TRANSPORT` | MCP 传输模式：`stdio`、`streamable-http`、`sse` | `stdio` |
| `HOST` | 绑定地址（http / sse 模式） | `0.0.0.0` |
| `PORT` | 端口（http / sse 模式） | `8000` |

## Token 生命周期（V1 OAuth）

| 项目 | 说明 |
|------|------|
| 有效期 | 约 180 天 |
| 自动刷新 | 不支持（API 限制） |
| 过期检测 | 内置，到期前 24 小时预警 |
| 续期方式 | 重新运行 `dida auth login` |
| 存储位置 | `~/.dida365-agent-mcp/token.json`（自动加载） |
