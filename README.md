# ForgeWise

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%E2%89%A53.11-blue.svg)](https://python.org)

> **English** | [한국어](README.ko.md) | [日本語](README.ja.md) | [中文](README.zh.md)

ForgeWise is an open-source, locally-run, MCP-native code assistant. It exposes
code analysis and GitLab operations to any [Model Context Protocol](https://modelcontextprotocol.io)
client (and a plain CLI), so an AI agent — or you — can explain code, review for
security and maintainability, generate tests, do root-cause analysis, and summarize
changes without sending your repository to a third-party service.

Analysis runs deterministically by default. You can optionally point ForgeWise at
a local Ollama model or any OpenAI-compatible endpoint to enrich the output; if no
model is configured, every tool still returns useful deterministic results.

## Features

**Code analysis** (deterministic, runs on a local checkout):

- **Explain** — summarize a file or line range; list classes and functions.
- **Review** — scan the repository for security and maintainability findings, with a pass/fail status.
- **Refactor & fix** — surface refactoring candidates and auto-fixable risky patterns.
- **Test generation** — produce a `pytest` skeleton for Python functions.
- **Vulnerability explanation / resolution** — describe risky patterns and suggested fixes.
- **Root-cause analysis** — extract stack frames and the error line from a log.
- **Summaries** — merge-request summary, merge commit message, code-review summary, discussion summary, issue description, and SDLC language/quality trends.
- **Chat** — retrieve repository context relevant to a question.

**GitLab API** (works against any GitLab instance via REST):

- Issues — create / get.
- Merge requests — create / get, plus commits, diffs, and pipelines.
- Pipelines — list jobs, and list / create / retry / cancel.
- Work items — create / get notes.
- Search — global search, label search, and semantic code search.
- Server version.

Mutating GitLab tools (anything that creates or changes data) are **disabled by
default** and require `FORGEWISE_ENABLE_MUTATIONS=1` to run.

## Installation

```bash
pip install forgewise
# or, with uv:
uv pip install forgewise
```

> Not yet on PyPI? See the [development](#contributing) section to run from source.

ForgeWise installs three commands:

| Command | Purpose |
| --- | --- |
| `forgewise` | CLI |
| `forgewise-mcp` | MCP server over stdio |
| `forgewise-http` | MCP server over HTTP, with OAuth |

## Usage

### CLI

```bash
forgewise --repo . review
forgewise --repo . explain forgewise/features.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . root-cause error.log
forgewise --repo . issue-description "login fails after deploy"
forgewise --repo . check        # exits 1 if any finding exists — useful in a gate
```

Every command prints JSON. Run `forgewise --help` for the full list.

### MCP (stdio)

Register ForgeWise with your MCP client:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

Each tool call is appended to `.forgewise/audit.jsonl` with the tool name and
arguments; argument keys that look like secrets are recorded as `[REDACTED]`.

### MCP (HTTP)

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

Endpoints:

- `POST /api/v4/mcp` — MCP JSON-RPC
- `GET /.well-known/oauth-authorization-server` — OAuth metadata
- `POST /oauth/register` · `GET /oauth/authorize` · `POST /oauth/token` — OAuth 2.0 flow
- `GET /healthz` — health check

### Configuration

GitLab tools read `GITLAB_BASE_URL` (default `https://gitlab.com`) and `GITLAB_TOKEN`.

To enable an LLM backend, set `FORGEWISE_LLM_BACKEND` to `ollama` or `openai`
(see [docs/configuration.md](docs/configuration.md) for the full variable list).

## Roadmap

ForgeWise is pre-1.0. Planned, not yet implemented:

- Publish to PyPI; container image and Helm chart.
- Multi-forge support beyond GitLab (GitHub, Bitbucket).
- OAuth refresh-token rotation and SSO (OIDC / SAML) options.
- Prometheus metrics and structured JSON logging.

See [ROADMAP.md](ROADMAP.md) for details.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Code of Conduct](CODE_OF_CONDUCT.md), and report security issues per
[SECURITY.md](SECURITY.md).

Local development:

```bash
uv sync --python 3.11 --extra dev
uv run --python 3.11 --extra dev python -m pytest   # 233 passed, 7 skipped (live GitLab E2E)
make check                                          # ruff + mypy + pytest
```

ForgeWise does not use GitHub Actions; all checks run through local gates (`make check`).

## License

[MIT](LICENSE) © keiailab
