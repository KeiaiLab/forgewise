# AGENTS.md — ForgeWise (Tier-3 프로젝트 override)

> **한국어 (canonical)** | [한국어 i18n copy](AGENTS.ko.md) | [日本語](AGENTS.ja.md) | [中文](AGENTS.zh.md)
>
> *AGENTS.md 는 한국어를 source-of-truth 로 유지합니다 — keiailab 거버넌스 §2 한국어 원칙 정합.*

> 본 문서는 글로벌 거버넌스 (Tier-1 `~/.claude/CLAUDE.md` + Tier-2 `~/.claude/standards/*.md`)
> 에 대한 ForgeWise 프로젝트 특이성 (Python 전용 스택) override 를 기술한다.
> RFC-0001 (글로벌 부트스트랩) 정합. 본 문서가 글로벌과 충돌할 경우 우선순위 §3 에
> 따라 **사용자 명시 지시 > Tier-3 (본 문서) > Tier-2 standards > Tier-1 글로벌**.

## 0. import 계층

```
@~/.claude/CLAUDE.md                      # Tier-1 (글로벌 원칙 + 메타규약)
@~/.claude/standards/principles.md        # Tier-2 (운영 원칙)
@~/.claude/standards/linting.md           # Tier-2 (린팅 — Go 전제, 본 문서에서 Python override)
@~/.claude/standards/testing.md           # Tier-2 (테스트 — Go 전제, 본 문서에서 Python override)
@~/.claude/standards/ci.md                # Tier-2 (로컬 4 계층)
@~/.claude/standards/adr.md               # Tier-2 (ADR 양식)
@~/.claude/standards/enforcement.md       # Tier-2 (강제·자가수정)
@./docs/specs/2026-05-21-forgewise-governance-and-ops-alignment-design.md  # S6 spec
```

## 1. ForgeWise 의 고유성 (Why a Tier-3 override exists)

ForgeWise 는 `keiailab` operator family 의 *유일한 Python 프로젝트*다. 자매 프로젝트:

| Repo | 언어 | 도메인 |
|---|---|---|
| `valkey-operator` | Go | Kubernetes operator (Valkey/Redis) |
| `postgres-operator` | Go | Kubernetes operator (PostgreSQL) |
| `mongodb-operator` | Go | Kubernetes operator (MongoDB) |
| `operator-commons` | Go | Kubernetes operator 공통 라이브러리 |
| **`forgewise`** | **Python 3.11+** | **MCP-native developer intelligence** |

따라서 글로벌 standards 의 Go 전제 gate (gofmt / go vet / golangci-lint / govulncheck) 가
직접 적용되지 않는다. 동일 *정합성 정신* 을 Python 스택으로 *번역* 한다. 일탈 사유는
ADR `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md` 에 정당화한다.

## 2. Python override matrix

| 항목 | 글로벌 (Go 전제) | ForgeWise (Python override) |
|---|---|---|
| 언어 | Go 1.22+ | **Python 3.11+** |
| 패키지 매니저 | `go mod` | **`uv` 0.4+** (SSOT: `pyproject.toml`) |
| 빌드 | `go build` | `uv build` (hatchling backend) |
| 린트 | `gofmt + go vet + golangci-lint` | **`ruff check + ruff format`** (rule set: E/F/I/UP/B/SIM, line-length 100) |
| 타입체크 | `staticcheck` | **`mypy --strict`** (`disallow_untyped_defs = true`) |
| 테스트 | `go test -race ./...` | **`pytest -q --strict-markers`** |
| 의존성 audit | `govulncheck` | **`pip-audit`** (graceful skip 시 `uv tool install pip-audit` 권장) |
| 게이트 매니저 | `lefthook` (Go templates) | **`lefthook` (Python templates)** — 본 저장소 `lefthook.yml` 가 SSOT |
| 보안 스캔 | (Go: `gosec` 후보) | **`detect-secrets`** + Python 보안 규칙 (`forgewise.security`) |

### 2.1 `pyproject.toml` SSOT 원칙

ruff / mypy / pytest 설정은 **모두 `pyproject.toml` 한 곳**에서 관리한다. 별개 설정 파일
(`ruff.toml`, `mypy.ini`, `pytest.ini`) 신규 추가 **금지** — config drift 방지.

### 2.2 MCP server 운영 (forgewise 고유)

다른 4 종 operator 는 Kubernetes controller-runtime 기반. ForgeWise 는 MCP server:

| Transport | Entry point | 용도 |
|---|---|---|
| stdio | `forgewise-mcp` | 로컬 MCP client (Claude Desktop, Cursor 등) |
| HTTP | `forgewise-http` | 원격 MCP client (FastAPI + uvicorn, OAuth 2.0 DCR) |

운영 인터페이스가 본질적으로 다르므로 *환경 변수 표* + *OAuth scope* + *MCP tool input schema*
는 별도 운영 문서 (`docs/installation.md` / `docs/configuration.md` / `docs/api-reference.md`)
에서 관리한다. 4 종 operator 의 CRD spec 과는 SSOT 가 분리된다.

## 3. ForgeWise 특이 정책

### 3.1 MCP tool input schema 정책

모든 MCP tool 의 input schema 는 **JSON Schema strict mode**:

- 모든 property 는 `type` 명시 (`string` / `integer` / `object` 등).
- `required` 배열 명시.
- `additionalProperties: false` 권장 (현재 일부 tool 미적용 — 후속 task).
- 한국어 description 필수 (글로벌 §2 한국어 원칙).

새 MCP tool 추가 시 `forgewise/tools.py` 의 `list_tool_definitions()` 에 `ToolDefinition`
entry 추가 + 4 곳 동시 갱신 (CONTRIBUTING.md 의 "Adding a New MCP Tool" 참조).

### 3.2 OAuth scope 정책

ForgeWise HTTP transport 는 GitLab OAuth 2.0 application 의 다음 scope 만 사용:

| Scope | 용도 | 비고 |
|---|---|---|
| `read_repository` | 코드 분석 (read-only) | 필수 |
| `read_api` | GitLab API 조회 (issue / MR / pipeline list) | 필수 |
| `api` (write) | 변경성 tool (`create_issue`, `create_merge_request`, `manage_pipeline`) | **선택** — `FORGEWISE_ENABLE_MUTATIONS=1` 시에만. 운영 환경에서는 별도 OAuth application 분리 권장. |

`write_repository` 는 **사용하지 않음** (코드 직접 수정은 patch preview + 사용자 승인 후
별도 PR 로 처리, 후속 task 영역).

### 3.3 ASGI uvicorn pin

`pyproject.toml` 의 `uvicorn>=0.38` pin 은 ASGI lifespan 안정성 확보 (uvicorn 0.30 이전
version 은 lifespan event loop 누수 known issue). Python 3.11+ 만 지원하므로 uvicorn `>=0.30`
보다 `>=0.38` 로 더 엄격하게 고정.

### 3.4 GitHub Actions 영구 금지 (RFC-0002)

`.github/workflows/` 디렉토리 신규 생성 **절대 금지**. `tests/test_governance.py` 의
`test_github_actions_are_not_present` 가 코드 레벨로 강제. 위반 시 `make check` FAIL.

## 4. PR 게이트 (글로벌 ci.md 4 계층의 Python instantiation)

| 게이트 | pre-commit | pre-push | Makefile | 리뷰어 |
|---|:---:|:---:|:---:|:---:|
| `ruff check --fix` (lint) | ✅ | — | `make lint` | ✅ |
| `ruff format --check` (format) | ✅ | — | (포함) | — |
| `detect-secrets` (secrets scan) | ✅ (graceful skip) | — | — | ✅ |
| `markdownlint-cli2` (md lint) | ✅ (graceful skip) | — | — | — |
| `commitlint` regex (Conventional Commits) | — | — (commit-msg) | — | ✅ |
| `dco-signoff` (DCO `Signed-off-by:`) | — | — (commit-msg) | — | ✅ |
| `mypy --strict` (typecheck) | — | ✅ | `make typecheck` | ✅ |
| `pytest -q` (test) | — | ✅ | `make test` | ✅ |
| `pip-audit` (dependency audit) | — | ✅ (graceful skip) | — | ✅ |
| `force-push-warn` | — | ✅ | — | — |

`lefthook.yml` 의 hook 정의가 SSOT. 변경은 PR 로 추적.

## 5. 자가수정 (§self-repair) 적용 범위

글로벌 enforcement.md §self-repair 의 ForgeWise 특이 적용:

### 5.1 허용

- `pyproject.toml` 의 사소한 옵션 누락 (예: 새 ruff rule 추가)
- `uv.lock` regeneration (`uv sync` 결과 반영)
- `.gitignore` 보강
- 테스트 fixture 의 typing 누락 (mypy strict 통과 위함)

### 5.2 금지

- `pyproject.toml` 의 `dependencies` / `requires-python` 메이저 변경
- 새 MCP tool 추가 (사용자 의도 명시 필요 — 4 곳 동시 갱신 정책)
- `forgewise/oauth.py` / `forgewise/audit.py` 변경 (보안 경계)
- `.secrets.baseline` 자동 갱신 (false positive 검토 필수)

### 5.3 검증 의무

자가수정 후:
1. 변경된 파일 `grep` 으로 ground-truth 확인 (CLAUDE.md §8 "Edit success ≠ 적용 보증")
2. `make check` 재실행
3. HANDOFF.md (있다면) 에 자가수정 내역 명시

## 6. ADR 양식

`docs/kb/adr/NNNN-slug.md`:

```markdown
# ADR NNNN: <decision title>

| Status | Accepted / Proposed / Deprecated / Superseded |
|---|---|
| Date | YYYY-MM-DD |
| Authors | <name <email>> |

## Context
...

## Decision
...

## Consequences
- (+) ...
- (-) ...

## References
- ...
```

현재 등록된 ADR:

| ID | Title | Status |
|---|---|---|
| 0001 | Python stack override vs global Go standards | Accepted (2026-05-21) |

## 7. 후속 작업 (placeholder)

- `forgewise.policy.json` 조직 정책 파일 도입 시 본 문서 §3 갱신.
- S5 commons 공통화 완료 시 `lefthook.yml` 을 `operator-commons/templates/lefthook-python.yml`
  로 분리하고 본 저장소는 `cp + customization` 패턴으로 재배포.
- Python `>= 3.12` 도입 시 `pyproject.toml` `requires-python` 및 `[tool.ruff]
  target-version` 동시 갱신 — 본 문서 §2 표 동기화 필수.

---

Signed-off-by: TaeHwan Park <eightynine01@gmail.com>
