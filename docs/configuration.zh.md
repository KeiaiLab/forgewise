# 配置 (Configuration)

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> [English](configuration.md) | [한국어](configuration.ko.md) | [日本語](configuration.ja.md) | **中文**

整理 ForgeWise 的运维接口 (MCP client 注册 / OAuth scope / GitLab 认证 /
audit log / mutation gate)。环境变量表参见 `docs/installation.md`。

## MCP client 注册

ForgeWise 提供两种 transport。

### stdio transport (`forgewise-mcp`)

与本地 MCP client (Claude Desktop, Cursor, Continue 等) 直接通信。无需额外认证
(client 以宿主 OS 的权限执行)。

Claude Desktop `claude_desktop_config.json` 示例:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp",
      "env": {
        "GITLAB_BASE_URL": "https://gitlab.example.com",
        "GITLAB_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Cursor `.cursor/mcp.json` 格式相同。

### HTTP transport (`forgewise-http`)

远程 MCP client + 多用户环境。FastAPI + uvicorn + OAuth 2.0 Dynamic Client
Registration。

```bash
forgewise-http --host 127.0.0.1 --port 8080 --require-oauth
```

CLI option:

| Option | 默认值 | 说明 |
|---|---|---|
| `--host` | `127.0.0.1` | bind address. 使用 0.0.0.0 时推荐 firewall + reverse proxy |
| `--port` | `8080` | bind port |
| `--require-oauth` | (off) | 强制 OAuth 2.0 认证. 生产环境推荐 (与 `FORGEWISE_REQUIRE_OAUTH=1` 等价) |
| `--workers` | `1` | uvicorn worker 数 (非 CPU bound,通常 1 个足够) |

MCP endpoint: `POST /api/v4/mcp` (GitLab MCP server 兼容 URL)。

## MCP tool input schema 策略

所有 33 种 tool 都是 JSON Schema strict mode。通用模式:

```json
{
  "name": "<tool_name>",
  "description": "<中文描述>",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string", "description": "仓库根目录路径。省略时使用服务器默认路径。"},
      "<param>": {"type": "<type>", "description": "<中文描述>"}
    },
    "required": ["<param>"]
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false
  }
}
```

`annotations.readOnlyHint`:

- `true` — 所有 read-only tool (Duo 18 种 + GitLab 查询 tool)
- `false` — 变更类 tool. 附加 `openWorldHint: true`. 需要
  `FORGEWISE_ENABLE_MUTATIONS=1`.

详细 tool 级别 schema 参见 `docs/api-reference.md`。

## OAuth 2.0 scope

需在 ForgeWise 的 GitLab OAuth 2.0 application 注册的 scope:

| Scope | 用途 | 必需? |
|---|---|---|
| `read_repository` | 代码分析 (read-only). 等同 git clone / file read. | yes |
| `read_api` | GitLab API 查询 (issue / MR / pipeline / search). | yes |
| `api` (write) | 变更类 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`). | **可选** — 仅在 `FORGEWISE_ENABLE_MUTATIONS=1` 时需要. 生产环境推荐分离独立的 OAuth application. |

### DCR endpoint

| Endpoint | Method | 用途 |
|---|---|---|
| `/oauth/register` | POST | Dynamic Client Registration. 注册 redirect URI. |
| `/oauth/authorize` | GET | 颁发 Authorization code (5 分钟有效) |
| `/oauth/token` | POST | Access token 交换 (1 小时有效) |
| `/oauth/.well-known/oauth-authorization-server` | GET | RFC 8414 metadata |

PKCE: 支持 `plain` / `S256`. 推荐 `S256`.

Redirect URI 允许模式:

- `https://*` (强制 TLS)
- `http://127.0.0.1:*` (localhost dev)
- `http://localhost:*` (localhost dev)

其他 scheme 的 client 注册本身被拒绝。

## GitLab API 认证

GitLab REST API 调用需要 token. ForgeWise 按以下优先级 resolve token:

1. **Tool argument** `gitlab_token` (per-call override)
2. **环境变量** `GITLAB_TOKEN` (服务器启动时)
3. (无) → tool 失败: `필수 인자가 없습니다: gitlab_token`

屏蔽策略: token 绝对不会记录到 audit log. 包含秘密值关键字 (`token` /
`secret` / `password` / `key`) 的 argument 会自动用 `[REDACTED]` 屏蔽.

## audit log

ForgeWise 将所有 tool 调用记录到 `.forgewise/audit.jsonl`.

### 位置

```
<repo_root>/.forgewise/audit.jsonl
```

每行 = 1 JSON object (JSONL). 格式:

```json
{
  "ts": "2026-05-21T10:30:00.000000Z",
  "tool": "code_review",
  "arguments": {"repo": ".", "gitlab_token": "[REDACTED]"},
  "result_summary": {"finding_count": 7, "severity_high": 2}
}
```

### 屏蔽规则

包含以下关键字的 argument key,其 value 自动替换为 `[REDACTED]`:

- `token` (例: `gitlab_token`)
- `secret` (例: `client_secret`)
- `password`
- `key` (例: `api_key`)

详细: 参见 `forgewise/audit.py:mask_secrets`。

### 轮转

ForgeWise 不提供 audit log 自动轮转。推荐使用 logrotate 或 cron job 定期归档
(例: 每周 1 次,gzip 压缩)。

## mutation gate

未设置 `FORGEWISE_ENABLE_MUTATIONS=1` 时,以下 tool 的调用被阻止:

| Tool | 影响 |
|---|---|
| `create_issue` | 新创建 GitLab issue |
| `create_merge_request` | 新创建 GitLab MR |
| `manage_pipeline` (`operation != list`) | pipeline create / retry / cancel |
| `create_workitem_note` | 新 Work item note |

阻止时 error message: `변경성 GitLab tool은 FORGEWISE_ENABLE_MUTATIONS=1일 때만
실행됩니다.`

生产环境推荐分离部署*只读* MCP application 和*可写* MCP application,
分别管理 OAuth scope + `FORGEWISE_ENABLE_MUTATIONS` 环境变量。

## smoke-gitlab 使用

`make smoke-gitlab` 对 live GitLab 实例调用 read-only tool 子集,验证连通性 + 权限.
是 CI 不存在环境下的*第 4 层 (手动 gate)*.

```bash
export FORGEWISE_LIVE_GITLAB_TOKEN=glpat-xxx
export FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise
make smoke-gitlab
```

输出示例:

```
== ForgeWise GitLab smoke test ==
[1/5] get_mcp_server_version ... OK (version: 0.1.0)
[2/5] get_issue (#1) ... OK
[3/5] search (scope=blobs, search='ForgeWise') ... OK (5 hits)
[4/5] search_labels ... OK (12 labels)
[5/5] get_merge_request_commits (!1) ... OK (3 commits)
PASS
```

变更类 tool 不包含在 smoke 中 (避免对生产环境的副作用)。

## 分析结果 — tool 计数

ForgeWise 0.1.0 共提供 **33 种 MCP tool**:

- **18 种 GitLab Duo Enterprise 对应** (全部 local,不调用外部 LLM)
- **15 种 GitLab MCP compatible** (GitLab API proxy)

详细目录参见 `docs/api-reference.md`。

## 下一步

- 安装: `docs/installation.md`
- API 目录: `docs/api-reference.md`
- 版本迁移: `docs/upgrade.md`
- 安全策略: `docs/security.md` + `SECURITY.md`
