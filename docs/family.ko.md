<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# keiailab operator family

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> 하나의 거버넌스 기준선을 공유하는 5 sister 프로젝트 — `operator-commons` (Go) 기반의 Kubernetes 오퍼레이터 3종 + MCP-native 개발자 인텔리전스 도구 1종 (`forgewise`, Python).

본 페이지는 **`forgewise`** 저장소에서 읽고 있는 family canonical cross-link 입니다.

## Family 개요

| 프로젝트 | 언어 | 도메인 | 상태 | 저장소 |
|---|---|---|---|---|
| **`postgres-operator`** | Go | Kubernetes 오퍼레이터 (PostgreSQL 18+) | active | https://github.com/keiailab/postgres-operator |
| **`mongodb-operator`** | Go | Kubernetes 오퍼레이터 (MongoDB 7.0+) | active | https://github.com/keiailab/mongodb-operator |
| **`valkey-operator`** | Go | Kubernetes 오퍼레이터 (Valkey 8.0+, Redis fork BSD-3) | active | https://github.com/keiailab/valkey-operator |
| **`operator-commons`** | Go | 3 오퍼레이터의 공유 Go 라이브러리 | v0.7.0 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | Python 3.11+ | MCP-native 개발자 인텔리전스 (GitLab Duo Enterprise 호환) | active (0.1.x alpha) | https://github.com/keiailab/forgewise |

## 공유 정책

5 프로젝트 모두는 stack 이 달라도 동일한 거버넌스 primitive 로 수렴합니다:

- **Apache-2.0** 전체 — SSPL 미사용, SaaS 표면 카피레프트 미사용
- **로컬 4 계층 게이트** — pre-commit + pre-push + Makefile + 리뷰어 증거 (`RFC-0002`, GitHub Actions 영구 금지)
- **i18n 4-lang** — README + canonical 문서 영어 / 한국어 / 日本語 / 中文 (cleanup supercycle Wave 4, 2026-05-21)
- **DCO + Conventional Commits** — 모든 commit 의 `Signed-off-by:` + `<type>(<scope>)?: <subject>` 양식
- **한국어 commit message + PR body** — keiailab 거버넌스 기준선 (`~/.claude/CLAUDE.md` §2)
- **Plan/Spec/ADR 추적** — 프로젝트별 `docs/plans/` + `docs/specs/` + `docs/kb/adr/`, 교차 프로젝트 거버넌스는 `~/.claude/rfcs/`

## `forgewise` 고유성

`forgewise` 는 family 의 유일한 비-Go 프로젝트입니다. Stack 차이는 다음에 문서화:

| 영역 | Operator family (Go) | `forgewise` (Python) |
|---|---|---|
| 패키지 매니저 | `go mod` | `uv` (SSOT: `pyproject.toml`) |
| Lint | `gofmt + go vet + golangci-lint` | `ruff check + ruff format` |
| Typecheck | `staticcheck` | `mypy --strict` |
| 테스트 러너 | `go test -race ./...` | `pytest -q --strict-markers` |
| Audit | `govulncheck` | `pip-audit` |
| 배포 | Helm chart + OLM bundle | PyPI 패키지 + 컨테이너 이미지 (GHCR, 예정) |
| 런타임 | Kubernetes controller-runtime | MCP 서버 (stdio + HTTP/FastAPI/OAuth 2.0 DCR) |

상세 일탈 사유 + override matrix: `AGENTS.md` (Tier-3 override) + `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md`.

## 금지 정책

- ❌ **release gate 용 GitHub Actions** — 로컬 4 계층 enforcement (RFC-0002 참조, 인시던트 I-2026-04-28: GHA billing SPOF)
- ❌ **upstream proprietary code 임베드** — `forgewise` 는 GitLab Duo Enterprise 의 *기능 호환 표면* 만 제공, Duo 상표 / proprietary code / 모델 가중치 미포함
- ❌ **MVP 의 외부 LLM 호출** — `forgewise` MVP 는 결정론적 (LLM 호출 0), 사내 LLM 라우터는 opt-in attach point 만
- ❌ **Roadmap 의 시간 기반 마감** — 대신 기능 체크리스트 + 완성도 %

## 시작점 (`forgewise` 특이)

| 작업 | Entry point |
|---|---|
| 설치 + 환경 검증 | [docs/installation.md](installation.md) |
| MCP client 설정 + OAuth | [docs/configuration.md](configuration.md) |
| 33 종 MCP tool 카탈로그 | [docs/api-reference.md](api-reference.md) |
| 업그레이드 / 마이그레이션 정책 | [docs/upgrade.md](upgrade.md) |
| 설계 컨텍스트 | [docs/design.md](design.md) |
| 보안 기준선 | [docs/security.md](security.md) + [SECURITY.md](../SECURITY.md) |
| 이슈 / 기능 요청 | https://github.com/keiailab/forgewise/issues |
| 설계 / 로드맵 논의 | https://github.com/keiailab/forgewise/discussions |
| 코드 기여 | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 보안 이슈 신고 | [SECURITY.md](../SECURITY.md) |
| 브랜드 / 보이스 | [BRANDING.md](../BRANDING.md) |
| 릴리스 이력 | [CHANGELOG.md](../CHANGELOG.md) |
| 프로젝트 특이 AI override | [AGENTS.md](../AGENTS.md) (Tier-3) |

## Cross-family 호환성

3 데이터베이스 오퍼레이터는 `github.com/keiailab/operator-commons` 를 동일 version 으로 import (현재 `v0.7.0+`). `forgewise` 는 operator-commons 를 import 하지 *않지만* (Go ↔ Python 경계) 다음을 공유:

- 거버넌스 기준선 (`~/.claude/CLAUDE.md` Tier-1)
- ADR / RFC / commit 컨벤션
- i18n 정책 (`operator-commons/docs/i18n/README.md` SSOT)
- 용어집 (`operator-commons/docs/i18n/glossary-{ko,ja,zh}.md`)
- pre-commit hook 패턴 (lefthook)

`operator-commons` 의 breaking change 는 3 Go 오퍼레이터의 동기 bump 필요 — `forgewise` 는 API 경계에서 영향 받지 않지만, `scripts/sync-from-commons.sh` 로 공유 lefthook / i18n / 거버넌스 갱신을 받을 수 있음.

## i18n

본 페이지 (및 모든 `forgewise` canonical 문서) 는 4 언어로 제공:

- [English](family.md) (canonical)
- **한국어** (본 파일)
- [日本語](family.ja.md)
- [中文](family.zh.md)

분쟁 시 영어 버전이 기술 내용에 권위 있음 (authoritative); 현지화 버전은 동일 결정을 현지어로 자연스럽게 반영.

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">
  © 2026 keiailab · <a href="../LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
