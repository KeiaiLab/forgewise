# Changelog

> **English** | [한국어](CHANGELOG.ko.md) | [日本語](CHANGELOG.ja.md) | [中文](CHANGELOG.zh.md)

All notable changes to ForgeWise are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **0.x 정책** — `0.x.y` 동안 minor 도 breaking change 가능 (alpha). `1.0.0` 이후
> SemVer 엄격 적용. 모든 breaking change 는 본 파일의 `### Changed` 또는 `### Removed`
> 섹션에 마이그레이션 가이드 (`docs/upgrade.md` 인용) 와 함께 기록한다.

## [Unreleased]

## [0.1.0] — 2026-05-28

### Added

- MCP server bootstrap: CLI (`forgewise`), stdio (`forgewise-mcp`), HTTP (`forgewise-http`)
- 33 MCP tools: 18 GitLab Duo compatible + 15 GitLab MCP server compatible
- GitLab REST API v4 client with token redaction and fail-closed mutation gate
- OAuth 2.0 Dynamic Client Registration with PKCE (plain + S256)
- OAuth refresh token rotation with 7-day expiry
- Audit logging (`.forgewise/audit.jsonl`) with automatic secret redaction and log rotation (10 MB, 5 files)
- Static analysis: Python symbol extraction, refactoring suggestions, test skeleton generation
- Security scanning: hardcoded-secret, python-eval, shell-true detection and fix suggestions
- LLM backend abstraction (`forgewise/llm.py`): Ollama + OpenAI-compatible dual support
- AI-enhanced tools (7): duo_chat, code_explanation, code_review, merge_request_summary, merge_commit_message_generation, issue_description_generation, root_cause_analysis
- MCP tool input schema validation (required + type checking, JSON-RPC -32602 on invalid params)
- Structured JSON logging with `FORGEWISE_LOG_LEVEL` environment variable
- Prometheus metrics exposition (`/metrics` endpoint, optional `prometheus-client`)
- HTTP rate limiting (60 req/min default), CORS middleware, global exception handler
- GitLab client connect/read timeout separation (`GITLAB_CONNECT_TIMEOUT`, `GITLAB_READ_TIMEOUT`)
- Dockerfile (multi-stage, Python 3.11-slim) + `.dockerignore` + `make docker-build`
- Helm chart (`charts/forgewise/`) for Kubernetes deployment with `existingSecret` support
- PyPI publish pipeline (`make publish`, `scripts/release.sh`)
- E2E test framework (`docker-compose.e2e.yml`, `scripts/gitlab-e2e-seed.sh`, 7 E2E tests)
- Test infrastructure: `conftest.py` shared fixtures, `pytest-cov` (86% coverage), 233 tests
- 5 governance documents (SECURITY, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG, AGENTS)
- 4 operational documents (installation, configuration, api-reference, upgrade)
- 4-language support (EN, KO, JA, ZH) with i18n glossaries
- lefthook-based local CI 4-tier gates (pre-commit, commit-msg, pre-push, Makefile)
- `.env.example` with 12 environment variables documented
- ADR-0001: Python stack override justification

### Security

- OAuth access tokens stored as SHA-256 hashes (not plaintext)
- OAuth client secrets hashed at registration
- `detect-secrets` + `pip-audit` enforced in dev dependencies (`.secrets.baseline` generated)
- stdio Content-Length parsing hardened against malformed headers and DoS
- ruff security rules (S/bandit) enabled

[Unreleased]: https://github.com/keiailab/forgewise/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/keiailab/forgewise/releases/tag/v0.1.0
