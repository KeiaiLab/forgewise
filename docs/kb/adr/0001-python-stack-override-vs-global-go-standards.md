# ADR 0001: Python 스택 override vs 글로벌 Go 전제 standards

| 메타 | 값 |
|---|---|
| Status | **Accepted** |
| Date | 2026-05-21 |
| Authors | TaeHwan Park <eightynine01@gmail.com> |
| Supersedes | (없음) |
| Superseded by | (없음) |

## Context

`keiailab` 조직의 글로벌 거버넌스 (Tier-1 `~/.claude/CLAUDE.md` + Tier-2
`~/.claude/standards/*.md`) 는 operator family 의 *주류 언어* 인 **Go** 를
전제로 작성되었다. 글로벌 standards 의 다수 조항이 Go 도구 (gofmt / go vet /
golangci-lint / govulncheck / staticcheck) 를 직접 인용한다.

**ForgeWise 는 `keiailab` operator family 의 유일한 Python 프로젝트**다 (자매
프로젝트 4종 — `valkey-operator`, `postgres-operator`, `mongodb-operator`,
`operator-commons` — 은 모두 Go). 따라서:

1. 글로벌 standards 의 Go 전용 게이트를 ForgeWise 에 *직접 적용 불가*.
2. 글로벌 standards 의 *정합성 정신* (lint + typecheck + test + audit + secrets +
   하나의 패키지 매니저 SSOT) 은 ForgeWise 에도 적용되어야 한다.
3. Python 생태계의 *대응 도구* 로 번역하여 동등한 안전망을 구축해야 한다.

또한 ForgeWise 는 *MCP-native server* 라는 별개 도메인 (FastAPI + uvicorn +
authlib + httpx + Python 3.11+) 으로, 4종 operator (controller-runtime 기반
Kubernetes operator) 와 운영 인터페이스가 본질적으로 다르다. 환경 변수 표 /
OAuth scope / MCP tool input schema 등은 별도 운영 문서가 필수.

S6 cycle (`docs/specs/2026-05-21-forgewise-governance-and-ops-alignment-design.md`)
에서 본 결정을 코드화하기 위한 *AGENTS.md (Tier-3) + lefthook.yml (Python) +
거버넌스 5종 + 운영 문서 4종 + 본 ADR* 가 한 묶음으로 도입되었다.

## Decision

ForgeWise 는 글로벌 Go 전제 standards 를 *프로젝트 특이성* 사유로 일탈한다. 일탈
범위 + 대체 게이트:

| 항목 | 글로벌 (Go 전제) | ForgeWise (Python override) |
|---|---|---|
| 언어 | Go 1.22+ | **Python 3.11+** |
| 패키지 매니저 | `go mod` | **`uv` 0.4+** (SSOT: `pyproject.toml`) |
| 빌드 | `go build` | `uv build` (hatchling backend) |
| 린트 | `gofmt + go vet + golangci-lint` | **`ruff check + ruff format`** (rule set: E/F/I/UP/B/SIM, line-length 100) |
| 타입체크 | `staticcheck` | **`mypy --strict`** (`disallow_untyped_defs = true`) |
| 테스트 | `go test -race ./...` | **`pytest -q --strict-markers`** |
| 의존성 audit | `govulncheck` | **`pip-audit`** (graceful skip 시 권장) |
| 게이트 매니저 | `lefthook` (Go templates) | **`lefthook` (Python templates)** — `lefthook.yml` SSOT |
| 보안 스캔 | (Go: `gosec` 후보) | **`detect-secrets`** + Python 보안 규칙 (`forgewise.security`) |

본 override 의 *기록부* 는 `AGENTS.md` (Tier-3 프로젝트 override 문서). 본 ADR 은
*정당화 문서*. 두 문서가 충돌할 경우 본 ADR 의 Status 가 우선.

## Consequences

### 긍정 (+)

- **Python 생태계 표준 도구 활용** — ruff (Rust 기반, 10-100x 빠른 linter),
  mypy strict (Python type 안전성 최강), uv (Rust 기반, pip 대비 10-100x 빠름),
  pip-audit (PyPA 공식 audit tool). 모두 active maintenance + community 지원.
- **operator-commons (Go 템플릿) 와 분리** — Python 전용 lefthook config 가
  forgewise 단독으로 유지보수됨. Go 템플릿 변경이 forgewise 에 영향 0.
- **재사용 가능 템플릿 source** — S5 commons 공통화 spec 진행 시 본 저장소의
  `lefthook.yml` 가 `operator-commons/templates/lefthook-python.yml` 의 원본
  후보. 향후 신규 Python 프로젝트 도입 시 부트스트랩 비용 절감.
- **글로벌 §1 원칙 정합 유지** — 글로벌 §1 "AI 는 초기 방향을 증폭한다 +
  안전장치 완성 후만 병렬" 의 *정신* 은 Python 도구로 번역되어 동일 효력. 글로벌
  원칙 자체를 일탈하지 않음.
- **사용자 시나리오 정합** — Python 개발자 (MCP client 통합, ML / DS 워크플로우)
  의 도구 선호와 일치.

### 부정 (-)

- **commons 공통화 시 Python 템플릿 별도 작성 필요** — S5 spec 진행 시
  추가 작업 비용. 다만 본 저장소의 `lefthook.yml` 를 그대로 활용 가능하므로
  비용은 *복사 + customization* 수준.
- **글로벌 standards 갱신 시 본 ADR 도 동기화 필수** — 글로벌 `linting.md` /
  `testing.md` / `ci.md` 가 Go 전제에서 *language-agnostic* 으로 진화하면
  본 ADR 의 정당성 약화. 향후 글로벌 RFC 0004+ 진행 시 본 ADR 의 *Superseded*
  여부 재평가 필요.
- **타 operator 와 게이트 명령어 차이** — `make check` (forgewise) vs
  `make test` (Go 4종) 등 일관성 깨짐 가능. CONTRIBUTING.md 와 `AGENTS.md` 의
  "Python override matrix" 로 명시적 안내하여 완화.
- **Tier-3 override 가 *전례* 가 됨** — 향후 다른 언어 (TypeScript, Rust 등)
  프로젝트 도입 시 같은 양식 override 가 누적될 수 있음. 본 ADR 이 *패턴*
  으로 인용될 가능성 인지하고 작성됨.

## Alternatives Considered

### Alt 1 — 글로벌 standards 의 *언어 agnostic* 으로 진화 후 forgewise 도입

**거부 사유**: 글로벌 standards 의 12 모듈은 현재 placeholder 단계 (`v3.0.1-stable`
의 정합 복원 패치 진행 중). language-agnostic 진화는 RFC 0004+ 의 사용자 협업
turn 으로 *수개월* 소요. forgewise 의 거버넌스 도입 시점이 미정 — *지금* 부트스트랩
필요. 글로벌 진화 완료 후 본 ADR 의 *Superseded* 검토.

### Alt 2 — forgewise 를 Go 로 rewrite

**거부 사유**: MCP server 의 주류 SDK 가 Python (FastAPI + authlib + httpx). Go
로 rewrite 시 외부 SDK 미사용 (DIY) + 사용자 시나리오 (Python 개발자) 와 어긋남.
ROI 음수.

### Alt 3 — forgewise 의 정합성 게이트 *생략*

**거부 사유**: 글로벌 §2 "테스트 없는 기능은 존재할 수 없다 (MUST)" + §5 "린트/
테스트 에러 상태로 commit = 실패" 정합 위반. *불가*.

## References

- 글로벌: `~/.claude/CLAUDE.md` §1~§8 (글로벌 거버넌스)
- 글로벌: `~/.claude/rfcs/0001-bootstrap.md` (RFC 부트스트랩 정합)
- 글로벌: `~/.claude/rfcs/0002-github-actions-permanent-ban.md` (GHA 금지)
- 글로벌 standards: `~/.claude/standards/{principles,linting,testing,ci,adr,enforcement}.md`
- 본 저장소 spec: `docs/specs/2026-05-21-forgewise-governance-and-ops-alignment-design.md`
- 본 저장소 Tier-3: `AGENTS.md`
- 본 저장소 게이트: `lefthook.yml` + `Makefile` + `pyproject.toml`
- 본 저장소 정책: `CONTRIBUTING.md` + `SECURITY.md` + `CODE_OF_CONDUCT.md` + `CHANGELOG.md`
- 본 저장소 운영: `docs/installation.md` + `docs/configuration.md` + `docs/api-reference.md` + `docs/upgrade.md`

---

Signed-off-by: TaeHwan Park <eightynine01@gmail.com>
