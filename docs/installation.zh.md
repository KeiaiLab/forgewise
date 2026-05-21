# 安装 (Installation)

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> [English](installation.md) | [한국어](installation.ko.md) | [日本語](installation.ja.md) | **中文**

ForgeWise 是基于 Python 3.11+ 的 MCP-native developer intelligence 服务器。本文档涵盖
安装 / 环境配置 / 验证 / 故障排查。

## 系统要求

| 项目 | 最低 | 推荐 |
|---|---|---|
| Python | 3.11 | 3.11 或 3.12 |
| `uv` | 0.4 | 0.5+ |
| 磁盘 | 50 MB | 200 MB (开发 + 缓存) |
| OS | Linux / macOS | Linux x86_64 (生产) |
| Memory | 256 MB | 1 GB (大规模仓库分析时) |

`pip` 单独环境也支持,但推荐使用 `uv` (lockfile 一致性、构建速度)。

## 快速安装

### Option 1 — `uv` (推荐)

开发用 (clone 仓库):

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
uv sync --extra dev
```

部署用 (PyPI 发布后,目前 unreleased):

```bash
uv tool install forgewise
```

### Option 2 — `pip`

开发用:

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

部署用 (PyPI 发布后):

```bash
pip install forgewise
```

## 环境变量

ForgeWise 的运行时行为通过以下环境变量控制。**星号 (*)** 表示生产环境必需。

| 变量 | 必需? | 默认值 | 说明 |
|---|---|---|---|
| `GITLAB_BASE_URL` | * | `https://gitlab.com` | GitLab CE/EE 实例 URL (例: `https://gitlab.example.com`) |
| `GITLAB_TOKEN` | * | (无) | GitLab API token (Personal Access Token 或 Project Access Token) |
| `FORGEWISE_ENABLE_MUTATIONS` | no | (未设置) | 设置为 `1` 时允许变更类 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`)。未设置时阻止。 |
| `FORGEWISE_REQUIRE_OAUTH` | no | (未设置) | 在 HTTP transport 强制 OAuth 2.0 认证。生产环境推荐 `1`。 |
| `FORGEWISE_LIVE_GITLAB_TOKEN` | no | (无) | `make smoke-gitlab` 专用 token (测试环境隔离) |
| `FORGEWISE_LIVE_PROJECT_ID` | no | (无) | `make smoke-gitlab` 的测试目标 project ID 或 full path |

### OAuth 2.0 应用变量 (HTTP transport)

| 变量 | 必需? | 说明 |
|---|---|---|
| `FORGEWISE_OAUTH_CLIENT_ID` | yes (HTTP + OAuth) | OAuth 2.0 client ID (使用 Dynamic Client Registration 时自动颁发) |
| `FORGEWISE_OAUTH_CLIENT_SECRET` | yes (HTTP + OAuth) | OAuth 2.0 client secret. 通过 `.env` 或 secret manager 注入. **绝对禁止 commit。** |
| `FORGEWISE_LOG_LEVEL` | no | `DEBUG` / `INFO` (默认) / `WARN` / `ERROR` |

### `.env` 格式示例

```bash
# .env (绝对禁止 commit — 加入 .gitignore)
GITLAB_BASE_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
FORGEWISE_ENABLE_MUTATIONS=
FORGEWISE_REQUIRE_OAUTH=1
FORGEWISE_OAUTH_CLIENT_ID=forgewise-prod
FORGEWISE_OAUTH_CLIENT_SECRET=...
FORGEWISE_LOG_LEVEL=INFO
```

## 验证

安装后立即用以下命令验证环境:

```bash
# 1. CLI 工作确认
forgewise --version
forgewise --repo . check

# 2. MCP stdio transport 启动 (Ctrl+C 退出)
forgewise-mcp

# 3. MCP HTTP transport 启动 (另一 shell,Ctrl+C 退出)
forgewise-http --host 127.0.0.1 --port 8080

# 4. 本地 gate (开发环境)
make check

# 5. GitLab live smoke (可选,需 GITLAB_TOKEN + FORGEWISE_LIVE_PROJECT_ID)
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise make smoke-gitlab
```

如果都是 zero exit code,环境正常。`make check` 验证 ruff + mypy + pytest 543 LOC。

## 故障排查

### OAuth 认证失败

症状: HTTP transport `/api/v4/mcp` 调用时 `401 Unauthorized`。

原因 / 对应:

1. `FORGEWISE_REQUIRE_OAUTH=1` 但 client 未传 token → 检查 `Authorization:
   Bearer <access_token>` header。
2. token 过期 (默认 1 小时) → 重新请求 `/oauth/token`。
3. redirect URI 不允许 → 仅允许 `https://` / `127.0.0.1` / `localhost`。其他
   scheme 的 client 注册本身被拒绝。
4. PKCE code_verifier 不匹配 → `S256` 时验证 base64url(SHA-256(verifier))。

详细参见 `docs/security.md` 的 OAuth 段落。

### GitLab 连接失败

症状: `GitLab API 호출 실패: HTTP 401` 或 `Connection refused`。

原因 / 对应:

1. `GITLAB_TOKEN` 未设置 → 检查 `.env` + `source .env` 或进程管理器的
   env 注入确认。
2. token 权限不足 → `read_repository` + `read_api` 最低。使用变更类 tool 时需
   `api` scope。
3. `GITLAB_BASE_URL` 拼写错误 → 包含 `https://`,推荐无 trailing slash。
4. self-signed cert → **禁止** 用 `httpx` 的 `verify=False` 绕过。将公司内 CA chain
   注册到系统 trust store。
5. network proxy → 确认 `HTTPS_PROXY` / `HTTP_PROXY` 环境变量正常设置。

### Python 版本不匹配

症状: `python: command not found` 或 `Python 3.10 detected, requires >= 3.11`。

对应:

```bash
# 使用 uv 时自动分离的 Python
uv python install 3.11

# 或 pyenv
pyenv install 3.11.10
pyenv local 3.11.10
```

`Makefile` 的 `PYTHON ?= 3.11` 可 override: `make check PYTHON=3.12`。

### mypy strict 失败

症状: `make check` 的 typecheck 阶段出现 `Function is missing a type annotation`。

对应: `pyproject.toml` 的 `[tool.mypy] strict = true` + `disallow_untyped_defs =
true` 是 SSOT. 新代码所有函数 signature 必须有 type annotation.
`# type: ignore[<code>]` 绕过须在 PR body 中说明理由.

### lefthook hook 未激活

症状: `git commit` 时 hook 输出 0.

对应:

```bash
# hook 安装确认
ls -la .git/hooks/pre-commit .git/hooks/pre-push .git/hooks/commit-msg

# 未安装时
make setup-hooks
```

`LEFTHOOK=0 git commit ...` 可全局绕过,但 PR 本文中必须说明理由。

## 下一步

- 环境配置详情: `docs/configuration.md`
- 33 种 MCP tool 目录: `docs/api-reference.md`
- 版本迁移: `docs/upgrade.md`
- 安全策略: `docs/security.md` + `SECURITY.md`
- 贡献指南: `CONTRIBUTING.md`
