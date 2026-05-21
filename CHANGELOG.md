# Changelog

> **English** | [한국어](CHANGELOG.ko.md) | [日本語](CHANGELOG.ja.md) | [中文](CHANGELOG.zh.md)

All notable changes to ForgeWise are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

> **0.x 정책** — `0.x.y` 동안 minor 도 breaking change 가능 (alpha). `1.0.0` 이후
> SemVer 엄격 적용. 모든 breaking change 는 본 파일의 `### Changed` 또는 `### Removed`
> 섹션에 마이그레이션 가이드 (`docs/upgrade.md` 인용) 와 함께 기록한다.

## [Unreleased]

### Added

- `AGENTS.md` — Tier-3 프로젝트 override (Python 스택 — ruff / mypy strict / uv /
  pyproject.toml SSOT). 글로벌 Go 전제 standards 와의 일탈을 ADR 0001 로 정당화.
- `CHANGELOG.md` — Keep a Changelog v1.1.0 + SemVer 양식.
- `CODE_OF_CONDUCT.md` — Contributor Covenant v2.1 외부 참조. 신고 채널 명시.
- `SECURITY.md` — 보안 신고 채널 + 응답 SLO + 알려진 보안 경계.
- `CONTRIBUTING.md` — 개발 환경 + Conventional Commits + DCO + PR flow + MCP tool
  추가 절차 + 로컬 4 계층 gate 설명.
- `lefthook.yml` — Python 4 계층 게이트 (ruff / mypy / pytest / detect-secrets /
  markdownlint / commitlint / DCO / pip-audit). RFC-0002 (GHA 금지) 정합.
- `Makefile` `setup-hooks` target — lefthook git hooks 1-step 설치.
- `docs/installation.md` — Python 3.11+ + uv 환경 + 환경 변수 표 (6 종) +
  troubleshooting.
- `docs/configuration.md` — MCP client 등록 (stdio + HTTP) + OAuth 2.0 DCR scope
  + GitLab API 인증 + audit log 정책 + mutation gate.
- `docs/api-reference.md` — 33 종 MCP tool 의 input/output schema 카탈로그
  (Duo 18 + GitLab compat 15). source: `forgewise/tools.py`
  `list_tool_definitions()`.
- `docs/upgrade.md` — SemVer 정책 + 향후 vN+1 → vN+2 마이그레이션 양식 (현재
  initial release 준비 중).
- `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md` — Python
  스택 override 결정 ADR. Status=Accepted.

### Changed

- `tests/test_governance.py` — 거버넌스 5 종 + 운영 4 종 + `lefthook.yml` +
  `AGENTS.md` 키워드 강제 assertion 추가.

### Deprecated

- (없음)

### Removed

- (없음)

### Fixed

- (없음)

### Security

- (없음 — 본 cycle 은 거버넌스/문서 범위. tool 코드 변경 0)

### Added (post-sync 2026-05-21)

- `.gitlab-ci.yml` — GitLab CI stand-alone pipeline (lint/typecheck/test 3 stage,
  RFC-0002 정합). pipeline-gated `merge_when_pipeline_succeeds=true` 활성.
- `pyproject.toml [tool.coverage.*]` + `pytest-cov` dev dep + `Makefile coverage`
  target — branch coverage + fail_under=70 alpha baseline (현재 76.49%).
- `tests/test_mcp_server.py` — LSP transport + main loop test 6 신규
  (mcp_server.py coverage 30% → 100%).

### Changed (post-sync 2026-05-21)

- `SECURITY.md` — PGP key URL 구체화 (org website 모호 →
  `keiailab.com/security/pgp-public-key.asc`).
- `README.{md,ko,ja,zh}.md` — "Contributing & Governance" 섹션 6 link 추가
  (Contributing/Security/Code of Conduct/Agents/Roadmap/Adopters). 4-lang sync.
- `Makefile audit-quality` target — `../operator-commons` 부재 시 graceful skip
  (OSS consumer 호환).
- `lefthook.yml py-audit` hook — `pip-audit` detection 강화 (pyenv shim silent
  fail 해소 — `command -v` → `pip-audit --version` 검사).

### Fixed (post-sync 2026-05-21)

- `tests/test_nim.py:22` — mypy strict 정합 (`_mock_response` return type
  annotation + `dict` generic argument).

## [0.1.0] - 2026-05-12

### Added

- MCP-native developer intelligence MVP (Python 3.11 / FastAPI / authlib /
  httpx / uvicorn).
- 18 GitLab Duo Enterprise tool + 15 GitLab MCP compatible tool = 총 33 종.
- stdio transport (`forgewise-mcp`) + HTTP transport (`forgewise-http`).
- OAuth 2.0 Dynamic Client Registration (PKCE plain / S256, redirect URI
  whitelist: `https://`, `127.0.0.1`, `localhost`).
- 결정론적 분석 (외부 LLM 미호출).
- `.forgewise/audit.jsonl` 감사 로그 + 비밀값 마스킹 (`token` / `secret` /
  `password` / `key` → `[REDACTED]`).
- `make check` 로컬 게이트 (ruff + mypy + pytest).
- `tests/test_governance.py` — `.github/workflows/` 부재 강제 (RFC-0002 정합).
- README 4-lang 구조 (en SSOT + ko 정식판 + ja/zh placeholder).
- `docs/design.md` + `docs/security.md` + `docs/references.md` +
  `docs/testing.md` + `docs/completion-audit.md`.

[Unreleased]: https://github.com/keiailab/forgewise/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/keiailab/forgewise/releases/tag/v0.1.0
