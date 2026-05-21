# ForgeWise

> [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **中文**

ForgeWise 是一个 `keiailab` 项目,以开源、本地可执行、MCP-native 的工具表面实现 GitLab Duo Enterprise 类的开发支援功能。

## 命名

选定名称为 **ForgeWise**。

- **Forge**: 面向所有代码 forge — GitLab、GitHub、Gitea、Forgejo。
- **Wise**: 不仅仅是聊天机器人,而是在统一的策略和审计日志之下执行代码解释、评审、安全说明、原因分析、测试生成和变更摘要。
- 避免直接使用 GitLab Duo 商标,仅以开源形式提供功能兼容的表面。

CLI 命令为 `forgewise`,stdio MCP 服务器命令为 `forgewise-mcp`,HTTP MCP 服务器命令为 `forgewise-http`。

## 功能表面

当前 MVP 以不调用外部 LLM 的确定性 (deterministic) 分析方式运行。同一个 API 表面在设计上可以后续接入企业内部 LLM 或 self-hosted 模型路由器。

| ForgeWise tool | 功能分组 |
| --- | --- |
| `code_suggestions` | 代码建议 |
| `duo_chat` | 仓库上下文 Chat |
| `code_explanation` | 代码解释兼容 alias |
| `code_explanation_ide` | IDE 代码解释 |
| `code_explanation_gitlab_ui` | GitLab UI 代码解释 |
| `refactor_code` | 重构建议 |
| `fix_code` | 修复建议 |
| `test_generation` | 测试生成 |
| `code_review` | 代码评审 |
| `root_cause_analysis` | 故障原因分析 |
| `vulnerability_explanation` | 漏洞说明 |
| `vulnerability_resolution` | 漏洞解决建议 |
| `merge_request_summary` | MR 摘要 |
| `discussion_summary` | 讨论摘要 |
| `sdlc_trends` | SDLC 质量趋势 |
| `merge_commit_message_generation` | Merge commit message 生成 |
| `code_review_summary` | 代码评审摘要 |
| `issue_description_generation` | Issue 描述生成 |

同时提供 GitLab MCP server 兼容 tool。

| ForgeWise tool | 对应的 GitLab MCP 功能 |
| --- | --- |
| `get_mcp_server_version` | MCP 服务器版本 |
| `create_issue`、`get_issue` | Issue 创建 / 查询 |
| `create_merge_request`、`get_merge_request` | MR 创建 / 查询 |
| `get_merge_request_commits`、`get_merge_request_diffs` | MR commit / diff 查询 |
| `get_merge_request_pipelines`、`get_pipeline_jobs`、`manage_pipeline` | Pipeline 查询 / 管理 |
| `create_workitem_note`、`get_workitem_notes` | Work item note 创建 / 查询 |
| `search`、`search_labels`、`semantic_code_search` | GitLab 搜索 |

## 安装

```bash
uv run --python 3.11 --extra dev python -m pytest
```

开发用安装:

```bash
uv sync --python 3.11 --extra dev
uv run forgewise --repo . review
```

## CLI 示例

```bash
forgewise --repo . explain forgewise/features.py
forgewise --repo . explain-ide forgewise/features.py
forgewise --repo . explain-ui forgewise/features.py
forgewise --repo . vuln-explain forgewise/security.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . issue-description "login failure after deploy"
forgewise --repo . check
```

如果存在任何安全或可维护性方面的 finding,`check` 会以退出码 (exit code) `1` 退出。

## MCP 服务器

向 MCP 客户端注册为 stdio 服务器:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

每次 tool 调用都会在 `.forgewise/audit.jsonl` 中记录 tool 名称、参数和功能名。键名看起来像机密信息的参数会在记录前用 `[REDACTED]` 屏蔽。

GitLab MCP 兼容的 HTTP endpoint 可如下启动:

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

HTTP endpoint:

- `POST /api/v4/mcp`: MCP JSON-RPC endpoint
- `POST /oauth/register`: Dynamic Client Registration
- `GET /oauth/authorize`: 授权码 (authorization code) 颁发
- `POST /oauth/token`: 访问令牌 (access token) 交换
- `GET /.well-known/oauth-authorization-server`: OAuth metadata

GitLab API tool 使用 `GITLAB_BASE_URL` 和 `GITLAB_TOKEN`。变更性 (mutation) tool 默认被禁用,启用需要 `FORGEWISE_ENABLE_MUTATIONS=1`。

## 本地 gate

不使用 GitHub Actions。所有验证都通过本地 gate 执行。

```bash
make check
```

Gate 构成:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

可选的 live smoke:

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=group/project make smoke-gitlab
```

未指定 token 和 project 时,smoke 以 skip 结束。

详细设计请参阅 [docs/design.md](docs/design.md),依据参考请参阅 [docs/references.md](docs/references.md),安全运维基准请参阅 [docs/security.md](docs/security.md)。

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">© 2026 keiailab · Apache-2.0 · <a href="https://keiailab.com">keiailab.com</a></p>
