# ForgeWise

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) | **中文**

ForgeWise 是一个 `keiailab` 项目,以开源、本地执行、MCP-native 工具表面方式
实现 GitLab Duo Enterprise 类开发辅助功能。

## 命名

选定名称为 **ForgeWise**。

- **Forge**: 面向所有 code forge — GitLab、GitHub、Gitea、Forgejo。
- **Wise**: 不是简单的聊天机器人,在相同策略和审计日志下执行代码解释、审查、
  安全解释、根因分析、测试生成、变更摘要。
- 不直接使用 GitLab Duo 商标,仅提供开源功能兼容表面。

CLI 命令为 `forgewise`,stdio MCP server 命令为 `forgewise-mcp`,HTTP MCP server
命令为 `forgewise-http`。

## 功能表面

当前 MVP 以确定性分析运行,不调用外部 LLM。同一 API 表面之上可以接入内部 LLM
或自托管模型路由器。

| ForgeWise tool | 功能组 |
| --- | --- |
| `code_suggestions` | 代码建议 |
| `duo_chat` | 仓库上下文 Chat |
| `code_explanation` | 代码解释兼容 alias |
| `code_explanation_ide` | IDE 代码解释 |
| `code_explanation_gitlab_ui` | GitLab UI 代码解释 |
| `refactor_code` | 重构建议 |
| `fix_code` | 修复建议 |
| `test_generation` | 测试生成 |
| `code_review` | 代码审查 |
| `root_cause_analysis` | 根因分析 |
| `vulnerability_explanation` | 漏洞解释 |
| `vulnerability_resolution` | 漏洞修复建议 |
| `merge_request_summary` | MR 摘要 |
| `discussion_summary` | 讨论摘要 |
| `sdlc_trends` | SDLC 质量趋势 |
| `merge_commit_message_generation` | Merge commit message 生成 |
| `code_review_summary` | 代码审查摘要 |
| `issue_description_generation` | Issue 描述生成 |

同时提供 GitLab MCP server 兼容 tool。

| ForgeWise tool | 对应 GitLab MCP 功能 |
| --- | --- |
| `get_mcp_server_version` | MCP server 版本 |
| `create_issue`, `get_issue` | Issue 创建 / 获取 |
| `create_merge_request`, `get_merge_request` | MR 创建 / 获取 |
| `get_merge_request_commits`, `get_merge_request_diffs` | MR commit / diff |
| `get_merge_request_pipelines`, `get_pipeline_jobs`, `manage_pipeline` | Pipeline 查询 / 管理 |
| `create_workitem_note`, `get_workitem_notes` | Work item note 创建 / 获取 |
| `search`, `search_labels`, `semantic_code_search` | GitLab 搜索 |

## 安装

```bash
uv run --python 3.11 --extra dev python -m pytest
```

开发安装:

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
forgewise --repo . issue-description "部署后登录失败"
forgewise --repo . check
```

如果存在安全或可维护性 finding,`check` 返回 exit code `1`。

## MCP 服务器

在 MCP 客户端中以 stdio 服务器形式注册:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

每次 tool 调用都会将 tool 名称、参数、功能名记录到 `.forgewise/audit.jsonl`。
看起来像秘密值的参数键在记录前会被自动 `[REDACTED]` 屏蔽。

GitLab MCP 兼容 HTTP endpoint 通过如下方式运行:

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

HTTP endpoint:

- `POST /api/v4/mcp`: MCP JSON-RPC endpoint
- `POST /oauth/register`: Dynamic Client Registration
- `GET /oauth/authorize`: authorization code 颁发
- `POST /oauth/token`: access token 交换
- `GET /.well-known/oauth-authorization-server`: OAuth metadata

GitLab API tool 使用 `GITLAB_BASE_URL` 和 `GITLAB_TOKEN`。变更类 tool 默认被禁用,
启用需要 `FORGEWISE_ENABLE_MUTATIONS=1`。

## 本地 gate

不使用 GitHub Actions。所有验证通过本地 gate 执行。

```bash
make check
```

Gate 组成:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

可选 live smoke:

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=group/project make smoke-gitlab
```

如果 token 和 project 不存在,smoke 以 skip 结束。

## 贡献与治理

- **贡献指南** — [CONTRIBUTING.md](CONTRIBUTING.md): 开发环境配置、Conventional Commits、DCO 签名、PR 流程。
- **安全** — [SECURITY.md](SECURITY.md): 漏洞报告、SLO、安全边界。
- **行为准则** — [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md): 社区标准 (Contributor Covenant 2.1)。
- **代理标准** — [AGENTS.md](AGENTS.md): 面向 AI 编码代理的 Tier-3 项目 override。
- **路线图** — [ROADMAP.md](ROADMAP.md): 计划功能与发布里程碑。
- **采用者** — [ADOPTERS.md](ADOPTERS.md): 在生产或评估中使用 ForgeWise 的组织。

详细设计请参见 [docs/design.md](docs/design.md),依据参考请参见
[docs/references.md](docs/references.md),安全运行基线请参见
[docs/security.md](docs/security.md)。

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
