# S6 Design: forgewise 거버넌스 + 운영 정합화

| 메타 | 값 |
|---|---|
| 날짜 | 2026-05-21 |
| 상태 | Proposed |
| 작성자 | keiailab — auto-cycle |
| 범위 | forgewise 단독 (valkey / postgres / mongodb / operator-commons 는 별 spec) |
| 후속 | 본 spec Accepted 시 `docs/plans/forgewise-governance-and-ops-alignment/INDEX.md` (writing-plans 산출) |
| 관련 spec | S1+ (valkey PR cleanup + GHA 제거), S2 (commons stale 정리), S3 (브랜딩), S4 (다국어), S5 (commons 공통화), S7 (postgres/mongodb GHA 제거) |
| author | TaeHwan Park <eightynine01@gmail.com> |

## 변경 이력

- **2026-05-21 v1.0**: 초기 작성. Status=Proposed. 사용자 명시 승인 후 Accepted 로 승격 예정.

## 1. 배경 (Background)

### 1.1 forgewise 의 고유성 — 다른 operator 4종과 다른 점

forgewise 는 keiailab operator family 의 *유일한* Python 프로젝트다 (다른 4 종 — valkey / postgres / mongodb / operator-commons — 은 모두 Go). 따라서 글로벌 standards 의 Go 전용 게이트 (`gofmt`, `go vet`, `golangci-lint`, `govulncheck`) 가 그대로 적용되지 않는다. 동일 *정합성 정신* 을 Python 스택 (ruff / mypy strict / pytest / detect-secrets) 으로 *번역* 한 lefthook + 거버넌스 5종 파일이 필요하다.

또한 forgewise 는 *MCP-native 서버* 라는 별개 도메인 (Python 3.11 / FastAPI / authlib / httpx / uvicorn) 으로, 운영 인터페이스가 4종 operator (controller-runtime 기반 Kubernetes operator) 와 본질적으로 다르다. 환경변수 표 / OAuth scope / MCP tool input schema 등은 별도 운영 문서가 필수.

### 1.2 현재 상태 — `ls -la` + `find` 측정 (2026-05-21)

| 항목 | 현황 | 비고 |
|---|---|---|
| `README.md` | 5,389 B | 영문 정식판 — Feature surface 표 + 설치 + CLI + MCP + Local Gates |
| `README.ko.md` | 4,754 B | 한국어 정식판 — 기능 표 한국어 |
| `README.ja.md` | 2,343 B | placeholder — 9 행 한자 깨짐 (`體크박스`) |
| `README.zh.md` | 2,022 B | placeholder — 9 행 한자 깨짐 (`复选框含义` 가 한국어 `복`을 닮음, 검증 필요) |
| `LICENSE` | MIT | 정상 |
| `docs/` | 5 파일 | design, security, references, testing, completion-audit |
| `Makefile` | 304 B | `lint / typecheck / test / check / smoke-gitlab` 5 target |
| `pyproject.toml` | 997 B | ruff (rule E/F/I/UP/B/SIM, line=100) + mypy strict + pytest |
| `tests/` | 8 파일 / 543 LOC | test_governance.py 포함 (GHA 부재 강제 작동 중) |
| `forgewise/` 모듈 | 14 .py | features, gitlab_client, http_server, oauth, mcp_server, tools 등 |
| `.github/workflows/` | **부재** | RFC-0002 정합 (이미 충족) |
| `.git/hooks/` (lefthook) | **부재** | lefthook.yml 없음 — 4 계층 중 1·2 계층 비활성 |
| `SECURITY.md` | **부재** | 거버넌스 핵심 파일 누락 |
| `CONTRIBUTING.md` | **부재** | 동상 |
| `CODE_OF_CONDUCT.md` | **부재** | 동상 |
| `CHANGELOG.md` | **부재** | 동상 |
| `AGENTS.md` | **부재** | Tier-3 프로젝트 override 부재 |
| `tests/test_governance.py` | 작동 | GHA workflow 부재 / 핵심 문서 키워드 검증 PASS |

### 1.3 강점

- `tests/test_governance.py` 가 *제대로 작동* — `.github/workflows` 디렉토리 존재 시 즉시 FAIL. RFC-0002 의 코드 레벨 강제. 5 종 operator 중 *유일하게* 거버넌스 테스트를 코드화한 저장소.
- `docs/` 5종 (design / security / references / testing / completion-audit) 이 *이미 한국어* 로 작성됨 — 글로벌 §2 한국어 원칙 충족.
- README 4-lang 골격이 *이미 존재* — placeholder 라도 navigation 구조 + 푸터 일관성은 갖춤.
- MIT LICENSE 정상.
- `pyproject.toml` 의 ruff/mypy 설정이 *최신 권장* (mypy strict + disallow_untyped_defs + ruff UP/B/SIM rule set).

### 1.4 핵심 결함 (gap)

| 결함 | 영향 | 우선순위 |
|---|---|---|
| 거버넌스 5 종 (SECURITY/CONTRIBUTING/COC/CHANGELOG/AGENTS) 부재 | OSS 신규 기여자 진입 차단 + 보안 신고 채널 부재 | P0 |
| `lefthook.yml` 부재 | 글로벌 4 계층 중 1+2 계층 (pre-commit / pre-push) 비활성 → DCO + Conventional Commits + secrets 누락 가능 | P0 |
| README.ja.md:9 한자 깨짐 (`體크박스`) | 일본어 사용자 불신 + 다른 4 종 정합성 어김 | P1 |
| README.zh.md 한자 의심 (검증 필요) | 중국어 사용자 불신 | P1 |
| 운영 문서 부재 (Installation / Configuration / API reference / Upgrade) | 자가 호스트 환경 셋업 시 README 한 곳만 참조 → 한계 | P1 |
| 4-lang switcher 가 README.md 상단에만 있고 다른 문서에 없음 | 다국어 사용자가 docs/ 진입 시 분기 끊김 | P2 |

## 2. 목표 (Goals) + 비목표 (Non-Goals)

### 2.1 Goals

| ID | 목표 | 검증 |
|---|---|---|
| G1 | 거버넌스 5 종 파일 신규 작성 (SECURITY / CONTRIBUTING / CODE_OF_CONDUCT / CHANGELOG / AGENTS) | `test -f SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md CHANGELOG.md AGENTS.md` 통과 |
| G2 | `lefthook.yml` 추가 + `make setup-hooks` Makefile target — Python 4 계층 활성 | `lefthook install` 후 `lefthook run pre-push` 통과 |
| G3 | README ja/zh 한자 깨짐 수정 + 4-lang switcher 푸터 일관성 | `grep -n '體' README.ja.md` 결과 0건 + 4-lang switcher 가 4 파일 모두 동일 양식 |
| G4 | 운영 문서 4 종 신규 (`docs/installation.md` / `docs/configuration.md` / `docs/api-reference.md` / `docs/upgrade.md`) | `test -f docs/{installation,configuration,api-reference,upgrade}.md` 통과 |
| G5 | `tests/test_governance.py` 갱신 — 거버넌스 5 종 + 운영 4 종 키워드 강제 | `make test` 통과 + 새 assertion 작동 |
| G6 | ADR 신규 — `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md` | Status=Accepted, RFC-0001 부트스트랩 인용 |
| G7 | 기존 `make check` 회귀 0 | `make check` 통과 + 543 LOC 테스트 전 통과 |

### 2.2 Non-Goals

- **S5 commons 공통화의 forgewise 측 작업**: helper 추출 / shared lefthook 분리 등은 별 spec (S5).
- **S4 다국어의 forgewise 본문 번역**: ja / zh 의 *placeholder 유지* 가 본 spec 의 입장. 본문 native 번역은 S4 사용자 native reviewer 협업 후. 본 spec 은 *깨진 한자 수정* + *navigation 구조* 까지만 보장.
- **MCP tool 신규 추가 또는 기존 동작 변경**: 본 spec 은 *문서 작성* 만. tool 코드는 1 byte 도 수정 안 함.
- **CI/CD 추가**: RFC-0002 영구 금지 그대로. `.github/workflows/` 디렉토리는 절대 만들지 않음.
- **detect-secrets 의 baseline 자동 생성**: lefthook 에 detect-secrets 등록만, baseline 생성은 별 후속 (운영 시 발생하는 false positive 를 case-by-case 로 allowlist).

## 3. 아키텍처 (단계 흐름)

```
[Phase 0] pre-flight (분석 재확인 + 기존 테스트 baseline)
   ↓
[Phase 1] lefthook.yml + Makefile setup-hooks target (Python 4 계층 활성)
   ↓
[Phase 2] 거버넌스 5 종 파일 신규 작성 (atomic 1 commit 가능, 또는 5 commit 분할)
   ↓
[Phase 3] README ja/zh 한자 깨짐 수정 + 4-lang switcher 일관성 + 푸터 동기화
   ↓
[Phase 4] 운영 문서 4 종 신규 (Installation / Configuration / API Reference / Upgrade)
   ↓
[Phase 5] tests/test_governance.py 갱신 — 신규 9 파일 키워드 강제
   ↓
[Phase 6] e2e — uv 환경에서 make check 통과 + lefthook run pre-push 통과
   ↓
[Phase 7] ADR + main tag (선택)
```

**원자성 (Atomic, CLAUDE.md §8)**: 본 spec 은 *문서 신규* 가 대부분이므로 Phase 별 commit 1 개 = task 1 개 원칙. 단 Phase 2 의 5 종 파일은 *논리적 단위* 가 같으므로 1 commit 으로 묶는다 (rationale: "거버넌스 골격 일괄 도입").

## 4. 단계별 상세 (Detailed Phases)

### Phase 0 — pre-flight (재확인)

- `git fetch origin && git pull --ff-only origin main` (이미 본 spec 작성 시 완료)
- `make check` baseline 통과 확인 (543 LOC 테스트 모두 통과 기대)
- `git status` clean 확인
- `uv` 설치 확인 (`uv --version`)
- 사용자 owner / admin 권한 확인 (PR 생성 + 머지 권한)

### Phase 1 — lefthook.yml + Makefile setup-hooks target

#### 1.1 lefthook.yml 신규

Python 스택 4 계층 (pre-commit / commit-msg / pre-push) 구성. *operator-commons 의 Go 전용 hook 제외* + Python 전용 hook 추가:

| 단계 | command | 도구 | 우회 |
|---|---|---|---|
| pre-commit | `py-lint` | `uv run ruff check --fix {staged_files}` (글로벌 `*.py`) | stage_fixed=true |
| pre-commit | `py-format` | `uv run ruff format --check {staged_files}` | — |
| pre-commit | `secrets` | `detect-secrets-hook --baseline .secrets.baseline {staged_files}` (baseline 없으면 graceful skip) | env `SECRETS_OK=1` |
| pre-commit | `md-lint` | `markdownlint-cli2 {staged_files}` (graceful skip if missing) | — |
| commit-msg | `commitlint` | Conventional Commits 정규식 검증 (`commitlint` 없으면 self-implemented regex) | `[skip-hooks]` |
| commit-msg | `dco-signoff` | `Signed-off-by:` line 존재 검증 | env `DCO_OK=1` (강력 비권장) |
| pre-push | `py-typecheck` | `uv run mypy --strict forgewise tests` | — |
| pre-push | `py-test` | `uv run python -m pytest -q` | — |
| pre-push | `py-audit` | `uv run pip-audit` (graceful skip if missing — `uv tool install pip-audit` 권장) | — |
| pre-push | `force-push-warn` | local 이 origin 보다 뒤일 때 warning | env `FORCE_PUSH_OK=1` |

**우회 정책 (글로벌 standards/ci.md TODO 와 연동)**: `LEFTHOOK=0` 또는 commit message `[skip-hooks]` 로 전체 우회 가능. 각 hook 별 개별 env 우회는 사유를 commit message / PR 본문에 의무 기술. detect-secrets baseline 누락 시 graceful skip (별 후속에서 baseline 생성).

**operator-commons 와의 SSOT 정합**: 본 lefthook.yml 은 *S5 commons 공통화* 가 완료되면 `operator-commons/templates/lefthook-python.yml` 로 분리되고 `cp + customization` 패턴으로 재배포된다. 본 spec 에서는 *forgewise 단독 hand-written* 으로 부트스트랩 — S5 spec 의 의존성 부재.

#### 1.2 Makefile setup-hooks target

```makefile
.PHONY: setup-hooks
setup-hooks:
	@command -v lefthook >/dev/null 2>&1 || { echo "lefthook 미설치 — brew install lefthook 또는 npm install -g lefthook"; exit 1; }
	lefthook install
	@echo "lefthook hooks 설치 완료. detect-secrets baseline 필요: 'detect-secrets scan > .secrets.baseline'"
```

기존 `check` target 에 의존성 추가 없음 (CI 부재 환경 동등 동작 보장).

#### 1.3 .gitignore 보강

`.secrets.baseline` 은 commit 대상 (allowlist 의 SSOT). `.lefthook-local.yml` (개발자별 우회) 는 ignore.

산출:
- `lefthook.yml` 신규
- `Makefile` 수정 (`setup-hooks` target 추가)
- `.gitignore` 보강
- `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md` 신규 (G6 — Phase 7 에서 finalize)

### Phase 2 — 거버넌스 5 종 파일 신규

#### 2.1 SECURITY.md

| 섹션 | 내용 |
|---|---|
| 지원 버전 | `0.1.x` (현재 alpha), 후속 `0.2.x` 도입 시 갱신 |
| 보안 신고 채널 | `security@keiailab.com` (조직 표준) + GitHub Security Advisory (private disclosure) |
| 응답 SLO | 영업일 기준 3 일 내 acknowledge, 30 일 내 patch 또는 mitigation 발표 |
| 알려진 보안 경계 | `docs/security.md` 인용 (OAuth scope / mutation gate / prompt injection) |
| CVE policy | 발견된 CVE 는 `CHANGELOG.md` Security 섹션에 기록 + Advisory 발행 |
| 비밀값 노출 시 | `.forgewise/audit.jsonl` 의 `[REDACTED]` 가 마스킹. 노출 의심 시 즉시 `GITLAB_TOKEN` revoke + 신고 |

#### 2.2 CONTRIBUTING.md

| 섹션 | 내용 |
|---|---|
| 개발 환경 | `uv` (Python 3.11) + `make setup-hooks` 1 회 실행 |
| 의존성 | `uv sync --extra dev` (ruff / mypy / pytest 설치) |
| commit 양식 | Conventional Commits (`feat: ...`, `fix: ...`, `docs: ...`) + DCO `Signed-off-by:` 강제 |
| 한국어 정책 | commit message / PR title / PR body / code 주석 = 한국어. 단 코드 식별자 / 표준 컨벤션 (Python PEP 8) 은 영문 |
| PR 절차 | 1) `make check` 통과 → 2) `lefthook run pre-push` 통과 → 3) PR 생성 → 4) PR template 의 체크리스트 5 항 충족 → 5) 사용자 리뷰 |
| 새 MCP tool 추가 | `forgewise/tools.py` 의 `ToolDefinition` + `tests/test_mcp_server.py` assertion + `docs/api-reference.md` 항목 + `docs/design.md` 기능 매핑 표 — 4 곳 모두 갱신 의무 |
| RFC-0002 / GHA 금지 | `.github/workflows/` 디렉토리 신규 절대 금지. 위반 시 `tests/test_governance.py` FAIL |
| Code of Conduct | `CODE_OF_CONDUCT.md` 준수 |

#### 2.3 CODE_OF_CONDUCT.md

Contributor Covenant v2.1 표준 영문 + 한국어 번역 병기 (organization 표준). 신고 채널 = `conduct@keiailab.com`.

#### 2.4 CHANGELOG.md

Keep a Changelog v1.1.0 + SemVer 양식. 초기 entry:

```
## [Unreleased]
### Added
- 거버넌스 5 종 파일 신규 (SECURITY/CONTRIBUTING/COC/CHANGELOG/AGENTS)
- lefthook.yml (Python 4 계층)
- 운영 문서 4 종 (Installation/Configuration/API Reference/Upgrade)

## [0.1.0] - 2026-05-12
### Added
- MCP-native developer intelligence MVP (Python 3.11 / FastAPI)
- 18 Duo Enterprise tool + 15 GitLab MCP compatible tool
- stdio (`forgewise-mcp`) + HTTP (`forgewise-http`) transport
- OAuth 2.0 Dynamic Client Registration
- 결정론적 분석 (외부 LLM 미호출)
- `make check` 로컬 게이트
```

#### 2.5 AGENTS.md (Tier-3 프로젝트 override)

글로벌 standards (Go 전제) 와 다른 부분만 명시:

| 항목 | 글로벌 | forgewise override |
|---|---|---|
| 언어 | Go (operator family) | **Python 3.11** |
| 빌드 | `go build` | `uv build` |
| 린트 | `gofmt + go vet + golangci-lint` | `ruff check + ruff format` |
| 타입체크 | `staticcheck` | `mypy --strict` |
| 테스트 | `go test -race` | `pytest -q` |
| 의존성 audit | `govulncheck` | `pip-audit` |
| 패키지 매니저 | `go mod` | `uv` |
| 게이트 매니저 | `lefthook (Go templates)` | `lefthook (Python templates)` — 본 spec 의 `lefthook.yml` 가 SSOT |
| MCP server | — | **forgewise 고유**: `forgewise-mcp` (stdio) + `forgewise-http` (FastAPI) |

import 디렉티브: `@~/.claude/CLAUDE.md` (글로벌 Tier-1 import). RFC-0001 부트스트랩 정합.

산출:
- `SECURITY.md` 신규
- `CONTRIBUTING.md` 신규
- `CODE_OF_CONDUCT.md` 신규
- `CHANGELOG.md` 신규
- `AGENTS.md` 신규
- 1 commit (논리적 단위 일괄) 또는 5 commit (atomic 극단) — 사용자 결정. **본 spec 의 권장 = 1 commit** (rationale: 5 종 파일은 독립적 의미가 없고 OSS 거버넌스 *골격* 일괄 도입).

### Phase 3 — README ja/zh 한자 깨짐 + 4-lang switcher + 푸터

#### 3.1 ja 한자 수정

- 라인 9: `RFC-0025 §1.2 體크박스 의미` → `RFC-0025 §1.2 チェックボックス 의미` (한국어 `체크박스` 의 한자 잔재 제거. 일본어 표기로 정정)
- 기타 한국어 잔재 (placeholder 라도) 점검:
  - 라인 8: `部分実装 (placeholder)` — `部分実装` 은 일본어 정상 (한자만 보면 한국어 `부분실장` 처럼 보이나 일본어 표기)
  - 라인 9 외 추가 `체` / `한` 한국어 한자 grep 검증

#### 3.2 zh 한자 수정

- 라인 8-9 의 `复选框含义` — 중국어 `복선상함의` 는 정상 한자 (`复选框` = 체크박스 中文). 단 한국어 한자와 *시각적으로 혼동* 가능 → native reviewer 검증 후 확정. 본 spec 에서는 *명백한 한국어 잔재만* 수정.
- `RFC-0025 §1.2 复选框含义` → 같은 의미로 유지 (수정 불필요 확률 高, 사용자 native 확인 후 결정).

#### 3.3 4-lang switcher 일관성

현재 4 파일 모두 상단에 nav 가 있고 푸터도 동일. 다음 점검:

- 4 파일 모두 라인 1 = `# ForgeWise` (일치)
- 라인 3 = nav 줄, 각 파일 자신 = **bold** (`**English**` / `**한국어**` / `**日本語**` / `**中文**`) 패턴 일관성 검증
- 푸터 (운영 family + © 2026) 4 파일 동일성 검증
- 차이 발견 시 ja/zh 를 정식판 패턴에 맞춤

#### 3.4 docs/ 5 종 한국어 문서의 다국어 분기

본 spec 의 *Non-Goal* 이므로 *문서 자체는 한국어 단일 유지*. 단 README 푸터에서 `docs/*` 진입 시 사용자가 "왜 docs/ 는 한국어만 있나" 의문을 가질 수 있음 → README ja/zh placeholder 본문에 명시: "docs/ 는 현재 한국어 SSOT. 다국어 번역은 S4 후속 spec 의 범위 (native reviewer 협업 필요)."

산출:
- `README.ja.md` 수정 (한자 깨짐 1+ 건)
- `README.zh.md` 점검 (수정 0~ 1 건, native confirm 후)
- `README.md`, `README.ko.md`, `README.ja.md`, `README.zh.md` 4 파일 nav + footer 동일성 보장
- 1 commit

### Phase 4 — 운영 문서 4 종 신규

#### 4.1 docs/installation.md

| 섹션 | 내용 |
|---|---|
| 시스템 요구 | Python 3.11+ / `uv` 0.4+ / 디스크 ~50 MB |
| 빠른 설치 | `uv tool install forgewise` (PyPI 게시 후) 또는 `git clone + uv sync` |
| 환경 변수 표 | `GITLAB_BASE_URL` / `GITLAB_TOKEN` / `FORGEWISE_ENABLE_MUTATIONS` / `FORGEWISE_REQUIRE_OAUTH` / `FORGEWISE_LIVE_GITLAB_TOKEN` / `FORGEWISE_LIVE_PROJECT_ID` 6 종 |
| 검증 | `forgewise --version` + `forgewise --repo . check` + `make smoke-gitlab` (선택) |
| 트러블슈팅 | `uv` 부재 → install 안내, mypy strict FAIL → `pyproject.toml` 의 `tool.mypy` 섹션 참조 |

#### 4.2 docs/configuration.md

| 섹션 | 내용 |
|---|---|
| 환경 변수 정리 | installation.md 의 표 인용 + 각 변수의 *동작 영향* 상세 |
| MCP client 등록 | stdio (`mcpServers.forgewise.command = forgewise-mcp`) + HTTP (`forgewise-http --host 127.0.0.1 --port 8080 --require-oauth`) |
| OAuth scope | `/oauth/register` (DCR) + `/oauth/authorize` (5 min code) + `/oauth/token` (1 hr access) + PKCE plain/S256 + redirect URI 허용 패턴 (`https://`, `127.0.0.1`, `localhost`) |
| GitLab API 인증 | `GITLAB_TOKEN` (env) vs `gitlab_token` (tool argument) 우선순위 + 마스킹 정책 |
| audit log | `.forgewise/audit.jsonl` 위치 + 마스킹 규칙 (`token` / `secret` / `password` / `key` 키워드 자동 `[REDACTED]`) |
| mutation gate | `FORGEWISE_ENABLE_MUTATIONS=1` 의 *영향 범위* (어떤 tool 이 차단되는지 명시) |

#### 4.3 docs/api-reference.md

33 종 tool 의 *input/output schema* 카탈로그 (현재 `forgewise/tools.py` 의 `list_tool_definitions` 인용):

**Local Duo Enterprise tools (18)**:
1. `code_suggestions`
2. `duo_chat`
3. `code_explanation` (alias)
4. `code_explanation_ide`
5. `code_explanation_gitlab_ui`
6. `refactor_code`
7. `fix_code`
8. `test_generation`
9. `code_review`
10. `root_cause_analysis`
11. `vulnerability_explanation`
12. `vulnerability_resolution`
13. `merge_request_summary`
14. `merge_commit_message_generation`
15. `code_review_summary`
16. `issue_description_generation`
17. `discussion_summary`
18. `sdlc_trends`

**GitLab MCP compatible tools (15)**:
19. `get_mcp_server_version`
20. `create_issue`
21. `get_issue`
22. `create_merge_request`
23. `get_merge_request`
24. `get_merge_request_commits`
25. `get_merge_request_diffs`
26. `get_merge_request_pipelines`
27. `get_pipeline_jobs`
28. `manage_pipeline`
29. `create_workitem_note`
30. `get_workitem_notes`
31. `search`
32. `search_labels`
33. `semantic_code_search`

**각 tool entry 양식**:
```markdown
### N. <tool_name>

**용도**: 1줄 설명
**input schema** (JSON):
- `repo` (string, optional): 저장소 루트 경로
- `<param>` (type, required/optional): 설명
**output**: `text` (JSON string) + `structuredContent` (object)
**예시 호출**: ...
**참조**: `forgewise/tools.py:<line>` + `docs/design.md:<section>`
```

#### 4.4 docs/upgrade.md

| 섹션 | 내용 |
|---|---|
| SemVer 정책 | `0.x.y` 동안 minor 도 breaking 가능, `1.0.0` 이후 SemVer 엄격 |
| 0.1.0 → 0.2.0 마이그레이션 | CHANGELOG.md 의 Breaking 섹션 인용 + 환경 변수 / MCP tool 이름 변경 시 매핑 표 |
| 의존성 갱신 | `uv sync --upgrade` + `make check` 회귀 검증 |
| MCP protocol 갱신 | `2025-03-26` / `2025-06-18` 협상 → 새 spec 도입 시 본 문서에 마이그레이션 가이드 추가 |
| 데이터 호환성 | `.forgewise/audit.jsonl` 양식 변경 시 자동 마이그레이션 스크립트 명세 |

산출:
- `docs/installation.md` 신규
- `docs/configuration.md` 신규
- `docs/api-reference.md` 신규
- `docs/upgrade.md` 신규
- 1 commit (4 종 일괄, "운영 문서 골격 도입")

### Phase 5 — tests/test_governance.py 갱신

기존 2 개 함수에 다음 추가:

```python
def test_governance_files_present() -> None:
    for name in ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "CHANGELOG.md", "AGENTS.md"):
        assert (ROOT / name).exists(), f"{name} missing"

def test_operational_docs_present() -> None:
    for name in ("installation.md", "configuration.md", "api-reference.md", "upgrade.md"):
        assert (ROOT / "docs" / name).exists(), f"docs/{name} missing"

def test_lefthook_yml_present() -> None:
    assert (ROOT / "lefthook.yml").exists()

def test_security_md_has_contact_channel() -> None:
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@keiailab.com" in security
    assert "Security Advisory" in security or "보안 신고" in security

def test_contributing_md_has_dco_requirement() -> None:
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "Signed-off-by" in contributing
    assert "Conventional Commits" in contributing or "Conventional" in contributing

def test_changelog_md_has_unreleased_section() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "[Unreleased]" in changelog or "Unreleased" in changelog
    assert "0.1.0" in changelog
```

산출:
- `tests/test_governance.py` 갱신 (기존 +6 assertion)
- 1 commit ("test: 거버넌스 + 운영 문서 키워드 강제")

### Phase 6 — e2e 검증

```bash
# 1. baseline + neuer 게이트 모두 통과
make check

# 2. lefthook 활성 후 pre-push 통과
make setup-hooks
lefthook run pre-push

# 3. governance + operational docs 신규 assertion 모두 PASS
uv run python -m pytest tests/test_governance.py -v

# 4. README 한자 깨짐 0 건
grep -n '體' README.ja.md && echo "FAIL: 한자 깨짐 잔존" || echo "PASS"

# 5. 4-lang switcher 일관성
for f in README.md README.ko.md README.ja.md README.zh.md; do
  head -5 "$f" | grep -E '^>'
done

# 6. 푸터 동일성
for f in README.md README.ko.md README.ja.md README.zh.md; do
  tail -3 "$f"
done

# 7. detect-secrets baseline (graceful skip if missing)
[ -f .secrets.baseline ] && detect-secrets-hook --baseline .secrets.baseline $(git ls-files '*.py' '*.md') || echo "baseline 미생성 — graceful skip"
```

모두 PASS 시 Phase 7 진입.

### Phase 7 — ADR + main tag

#### 7.1 ADR

`docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md`:

| 섹션 | 내용 |
|---|---|
| Status | Accepted |
| Date | 2026-05-21 |
| Context | 글로벌 standards/ 모듈 (특히 linting.md / testing.md / ci.md) 가 Go 스택 기준으로 작성 중. forgewise 는 유일한 Python 프로젝트로 직접 적용 불가. |
| Decision | AGENTS.md 에 Python override 명시 + lefthook.yml 의 Python 전용 hook + Makefile target = ruff / mypy strict / pytest / pip-audit. |
| Consequences | (+) Python 생태계 표준 도구 사용, (+) operator-commons 의 Go 템플릿과 분리, (-) S5 commons 공통화 시 Python 템플릿 별도 작성 필요. |
| References | RFC-0001 (글로벌 부트스트랩), RFC-0002 (GHA 금지), 본 spec. |

#### 7.2 main tag (선택)

`git tag v0.1.1` (CHANGELOG.md 의 Unreleased → 0.1.1 승격 후) — 사용자 결정 시점.

산출:
- `docs/kb/adr/0001-...md` 신규
- (선택) `v0.1.1` tag

## 5. 리스크 & 완화

| 리스크 | 영향 | 완화 |
|---|---|---|
| Python vs Go 정합 패턴 차이 — 일부 글로벌 standards 가 Go 전용 | forgewise 가 글로벌 룰 *모두* 충족 못 함 | AGENTS.md 에 Python override 명시 + ADR 0001 정당화 |
| lefthook detect-secrets false positive | 합법적 코드 (예: 테스트 fixture token) 가 차단 | `.secrets.baseline` allowlist 초기 설정 별 후속 task + 본 spec 은 graceful skip 으로 진행 |
| 4-lang README 의 native reviewer 부재 | ja / zh 한자 수정의 정확성 검증 불가 | ja / zh 는 placeholder 유지 + glossary cross-link (operator-commons/docs/i18n) + 명백한 한국어 잔재만 수정. native 본문 번역은 S4 spec |
| CONTRIBUTING.md 의 DCO 강제 정책 변경 | 기존 contributor 의 commit 패턴 변경 강제 | CHANGELOG.md 의 Unreleased 에 명시 + AGENTS.md 의 override 에 명시 + lefthook commit-msg 의 우회 옵션 (`DCO_OK=1`, 단 강력 비권장) |
| pip-audit / markdownlint 도구 부재 환경 | lefthook pre-push 미통과 | graceful skip (`command -v ... || echo "graceful skip"`) + CONTRIBUTING.md 에 설치 안내 |
| 거버넌스 5 종 일괄 1 commit vs atomic 5 commit | atomic 원칙 (CLAUDE.md §8) 위반 의심 | 본 spec 권장 = 1 commit (rationale 명시) + 사용자 결정 시점에 5 commit 분할 가능 — Phase 2 의 commit 단위는 사용자 승인 후 finalize |
| `forgewise.policy.json` (design.md "후속 확장") 미구현 → CONTRIBUTING.md 의 *조직 정책* 명시 모호 | 향후 도입 시 본 문서 갱신 필요 | CONTRIBUTING.md 에 "정책 파일 도입 후 후속 갱신" 명시 |
| `tests/test_governance.py` 의 새 assertion 이 *문서 *체결성* 만 검증* → 내용 quality 미보장 | 문서가 형식적 placeholder 로 남을 위험 | CONTRIBUTING.md 의 PR template 에 *내용 충실도 체크* 항 추가 + 사용자 리뷰 의무화 |

## 6. 성공 기준 (Success Criteria)

본 spec 은 다음 모두 충족 시 *Implemented*:

```bash
# 1. 거버넌스 5 종 파일 존재
test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CODE_OF_CONDUCT.md && test -f CHANGELOG.md && test -f AGENTS.md

# 2. lefthook.yml 존재 + setup-hooks target
test -f lefthook.yml && grep -q "setup-hooks" Makefile

# 3. README ja/zh 한자 깨짐 0
test $(grep -c '體' README.ja.md) -eq 0

# 4. 운영 문서 4 종 존재
test -f docs/installation.md && test -f docs/configuration.md && test -f docs/api-reference.md && test -f docs/upgrade.md

# 5. tests/test_governance.py 신규 assertion 통과
uv run python -m pytest tests/test_governance.py -v

# 6. 기존 make check 회귀 0
make check

# 7. lefthook pre-push 통과 (graceful skip 허용)
make setup-hooks && lefthook run pre-push

# 8. ADR 0001 Accepted
grep -A1 'Status' docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md | grep -q Accepted
```

증거 보존:
- 각 phase 종료 시 PR description / commit body 에 명령어 + 출력 인용 (CLAUDE.md §2 "통과 로그·핵심 출력을 인용해 입증")
- main commit log + ADR 0001 = 영구 흔적

## 7. 본 spec 의 out-of-scope (별 sub-project)

| 항목 | 분류 | 비고 |
|---|---|---|
| operator-commons 공통화 시 forgewise 측 helper 분리 | S5 | 별 spec. 본 spec 의 `lefthook.yml` 가 S5 의 *Python 템플릿 원본 후보* |
| forgewise 본문 다국어 번역 (ja / zh) | S4 | 별 spec. 본 spec 은 placeholder 유지 + 한자 깨짐 수정만 |
| MCP tool 코드 변경 / 신규 tool | 별 cycle | 본 spec 은 *문서 작성* 만, tool 코드 1 byte 도 미수정 |
| valkey-operator PR cleanup + GHA 제거 | S1+ | 별 spec, 병렬 가능 |
| postgres / mongodb GHA 제거 | S7 | 별 spec, 병렬 가능 |
| 5 종 저장소 브랜딩 통일 | S3 | 별 spec, 본 spec 의 README 푸터 (operator family + © 2026) 는 S3 의 *forgewise 측 적용분* — 이미 적용 됨 |
| commons stale 브랜치 정리 | S2 | 별 spec, 독립 |
| forgewise PyPI 게시 + GitHub Release | 후속 cycle | RFC-0002 의 예외 ③ (release tag → GitHub Release) 적용 시점에 별 spec |
| `forgewise.policy.json` 조직 정책 파일 | 후속 cycle | design.md "후속 확장" 항목, 본 spec 의 CONTRIBUTING.md 에 future 명시 |

## 8. 다음 단계

1. 사용자 본 design 검토 + Accepted 승격 (PR comment 또는 직접 답변)
2. 승인 후 `superpowers:writing-plans` skill 호출 → `docs/plans/forgewise-governance-and-ops-alignment/INDEX.md` + `research/*.md` 작성
3. plan 의 각 phase atomic 실행 (CLAUDE.md §8: task 1개 = 1 commit + 1 ship)
4. 각 phase 종료 시 PR 본문 / commit body 에 verification 증거
5. 완료 후 본 spec Status `Proposed → Implemented` 갱신 + ADR 0001 Accepted

## 부록 A. 정의 (Definitions)

- **로컬 4 계층** (RFC-0002): pre-commit hook · pre-push hook · Makefile target · PR 리뷰어 증거 확인
- **atomic** (CLAUDE.md §8): task 1개 = 1 commit + 1 ship + 1 deploy
- **거버넌스 5 종**: SECURITY / CONTRIBUTING / CODE_OF_CONDUCT / CHANGELOG / AGENTS
- **운영 문서 4 종**: Installation / Configuration / API Reference / Upgrade
- **DCO**: Developer Certificate of Origin — `Signed-off-by: Name <email>` line
- **Tier-3 override**: 프로젝트 AGENTS.md 가 글로벌 standards 의 specific 조항을 *프로젝트 특이성* 사유로 일탈 — ADR 정당화 필수

## 부록 B. 참조

- `~/.claude/CLAUDE.md` §1~§8 (글로벌 거버넌스)
- `~/.claude/rfcs/0001-bootstrap.md` (RFC 부트스트랩 정합)
- `~/.claude/rfcs/0002-github-actions-permanent-ban.md` (GHA 금지)
- `~/.claude/standards/{principles,linting,testing,ci,adr,enforcement}.md` (글로벌 standards)
- forgewise 본 저장소: `README.md`, `docs/design.md`, `docs/security.md`, `docs/references.md`, `docs/testing.md`, `docs/completion-audit.md`, `tests/test_governance.py`
- 자매 spec: S1+ (valkey), S2 (commons), S3 (브랜딩), S4 (다국어), S5 (commons 공통화), S7 (postgres+mongodb GHA)

---

Signed-off-by: TaeHwan Park <eightynine01@gmail.com>
