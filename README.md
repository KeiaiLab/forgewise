# ForgeWise

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://python.org)

> **English** | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

ForgeWise is a `keiailab` project that implements GitLab Duo Enterprise-class
development assistant features as an open-source, locally executable, MCP-native
tool surface.

## Naming

The chosen name is **ForgeWise**.

- **Forge**: targets all code forges — GitLab, GitHub, Gitea, Forgejo.
- **Wise**: not a simple chatbot — performs code explanation, review, security
  explanation, root-cause analysis, test generation, and change summarization
  under the same policy and audit log.
- Avoids direct use of the GitLab Duo trademark; provides only an open-source
  feature-compatible surface.

The CLI command is `forgewise`, the stdio MCP server command is `forgewise-mcp`,
and the HTTP MCP server command is `forgewise-http`.

## Feature Surface

The current MVP operates with deterministic analysis, without external LLM
calls. The same API surface is designed to allow attaching an in-house LLM or
self-hosted model router.

| ForgeWise tool | Feature group |
| --- | --- |
| `code_suggestions` | Code suggestions |
| `duo_chat` | Repository-context Chat |
| `code_explanation` | Code explanation compatible alias |
| `code_explanation_ide` | IDE code explanation |
| `code_explanation_gitlab_ui` | GitLab UI code explanation |
| `refactor_code` | Refactoring suggestions |
| `fix_code` | Fix suggestions |
| `test_generation` | Test generation |
| `code_review` | Code review |
| `root_cause_analysis` | Root-cause analysis |
| `vulnerability_explanation` | Vulnerability explanation |
| `vulnerability_resolution` | Vulnerability resolution suggestions |
| `merge_request_summary` | MR summary |
| `discussion_summary` | Discussion summary |
| `sdlc_trends` | SDLC quality trends |
| `merge_commit_message_generation` | Merge commit message generation |
| `code_review_summary` | Code review summary |
| `issue_description_generation` | Issue description generation |

GitLab MCP server compatible tools are also provided.

| ForgeWise tool | Corresponding GitLab MCP feature |
| --- | --- |
| `get_mcp_server_version` | MCP server version |
| `create_issue`, `get_issue` | Issue create / get |
| `create_merge_request`, `get_merge_request` | MR create / get |
| `get_merge_request_commits`, `get_merge_request_diffs` | MR commit / diff |
| `get_merge_request_pipelines`, `get_pipeline_jobs`, `manage_pipeline` | Pipeline query / manage |
| `create_workitem_note`, `get_workitem_notes` | Work item note create / get |
| `search`, `search_labels`, `semantic_code_search` | GitLab search |

## Installation

```bash
uv run --python 3.11 --extra dev python -m pytest
```

Development install:

```bash
uv sync --python 3.11 --extra dev
uv run forgewise --repo . review
```

## CLI Examples

```bash
forgewise --repo . explain forgewise/features.py
forgewise --repo . explain-ide forgewise/features.py
forgewise --repo . explain-ui forgewise/features.py
forgewise --repo . vuln-explain forgewise/security.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . issue-description "login failure after deploy"
forgewise --repo . check
```

`check` exits with code `1` if security or maintainability findings exist.

## MCP Server

Register as a stdio server in your MCP client:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

Each tool call logs the tool name, arguments, and feature name to
`.forgewise/audit.jsonl`. Arguments whose keys look like secrets are masked as
`[REDACTED]` before being recorded.

Run the GitLab MCP compatible HTTP endpoint as follows:

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

HTTP endpoints:

- `POST /api/v4/mcp`: MCP JSON-RPC endpoint
- `POST /oauth/register`: Dynamic Client Registration
- `GET /oauth/authorize`: authorization code issue
- `POST /oauth/token`: access token exchange
- `GET /.well-known/oauth-authorization-server`: OAuth metadata

The GitLab API tools use `GITLAB_BASE_URL` and `GITLAB_TOKEN`. Mutating tools
are blocked by default; to enable them, `FORGEWISE_ENABLE_MUTATIONS=1` is
required.

## Local Gates

GitHub Actions is not used. All verification runs through local gates.

```bash
make check
```

Gate composition:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

Optional live smoke:

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=group/project make smoke-gitlab
```

If the token and project are absent, smoke exits as skip.

For detailed design see [docs/design.md](docs/design.md); for grounding
references see [docs/references.md](docs/references.md); for security
operating standards see [docs/security.md](docs/security.md).

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
