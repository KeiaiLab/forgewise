# 변경 이력 (Changelog)

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> [English](CHANGELOG.md) | **한국어** | [日本語](CHANGELOG.ja.md) | [中文](CHANGELOG.zh.md)

ForgeWise 의 모든 주목할 만한 변경은 본 파일에 기록됩니다.

형식은 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 에 기반하며,
본 프로젝트는 [Semantic Versioning](https://semver.org/spec/v2.0.0.html) 을
준수합니다.

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
- **S4-D (2026-05-21)**: i18n 4-lang 정합
  - `BRANDING.{md,ko,ja,zh}.md` 신규 (forgewise 브랜드 정체성 + 상표 고지)
  - `docs/family.{md,ko,ja,zh}.md` 신규 (5 repo cross-link canonical)
  - `README.{ja,zh}.md` placeholder → 본문 완전 번역
  - `docs/installation.{ko,ja,zh}.md` 신규
  - `docs/configuration.{ko,ja,zh}.md` 신규
  - `docs/api-reference.{ko,ja,zh}.md` 신규 (33 종 MCP tool 전체 번역)
  - `docs/upgrade.{ko,ja,zh}.md` 신규
  - 거버넌스 5종 `SECURITY/CONTRIBUTING/CODE_OF_CONDUCT/CHANGELOG/AGENTS.{ko,ja,zh}.md` 신규
    (ja/zh 는 placeholder, ko 는 완전 번역)
- **S5 (post-sync, 2026-05-21)**: CI 게이트 + coverage + 신고 채널 보강
  - `.gitlab-ci.yml` 신규 — GitLab CI stand-alone (lint/typecheck/test 3-stage, RFC-0002 정합).
    pipeline-gated `merge_when_pipeline_succeeds=true` 활성.
  - `pyproject.toml [tool.coverage.*]` + `pytest-cov` dev dep + `Makefile coverage` target
    (branch coverage + fail_under=70 alpha baseline, 현재 76.49%)
  - `tests/test_mcp_server.py` — LSP transport + main loop test 6 신규
    (mcp_server.py coverage 30% → 100%)

### Changed

- `tests/test_governance.py` — 거버넌스 5종 + 운영 4종 + `lefthook.yml` +
  `AGENTS.md` 키워드 강제 assertion 추가.
- 거버넌스 5종 + 운영 4종 canonical (EN) 에 language banner (en/ko/ja/zh) 추가.

### Deprecated

- (없음)

### Removed

- (없음)

### Fixed

- (없음)

### Security

- (없음 — 본 cycle 은 거버넌스/문서 범위. tool 코드 변경 0)

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
