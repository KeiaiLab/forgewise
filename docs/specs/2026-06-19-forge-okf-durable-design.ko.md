# 설계: Forge 중립 provider + Harbor surface + OKF 지식 레이어 + 영속 장기작업

> 정본: 영어. 번역: [English](2026-06-19-forge-okf-durable-design.md).

| 메타 | 값 |
|---|---|
| 날짜 | 2026-06-19 |
| 상태 | Proposed |
| 작성자 | keiailab — design cycle |
| 범위 | forgewise 단독 (valkey / postgres / mongodb / operator-commons 는 별 spec) |
| 후속 | 본 spec Accepted 시 `docs/plans/forge-okf-durable/INDEX.md` (writing-plans 산출) |
| 관련 | `docs/design.md` (현 아키텍처), `ROADMAP.md` (v0.2+ multi-instance / caching / SLSA L3) |
| author | keiailab <noreply@keiailab.com> |

## 변경 이력

- **2026-06-19 v1.0**: 초기 작성. Status=Proposed. 사용자 명시 승인 후 Accepted 로 승격 예정.

## 1. 배경 (Background)

### 1.1 출발점

ForgeWise 는 현재 GitLab Duo Enterprise 기능군을 특정 상용 forge 에 묶지 않고
로컬 CLI + MCP 서버로 재구성한 프로젝트다 (`docs/design.md`). `forgewise/tools.py`
의 통합 카탈로그에 **33 개 MCP tool** (GitLab REST 호환 surface 15 + Duo 호환
surface 18) 을 담고, 두 transport — stdio (`forgewise-mcp`) 와 HTTP
(`forgewise-http`, FastAPI, `/api/v4/mcp`) — 그리고 `forgewise` CLI 로 노출한다.
기본 동작은 오프라인, 결정론적이며 외부 LLM 을 호출하지 않는다.

ForgeWise 는 **keiailab family 의 5번째 repo** 다 — operator 4 종
(postgres / mongodb / valkey-operator + operator-commons, 모두 Go) + forgewise
(유일한 Python 프로젝트). 본 설계가 참조하는 MongoDB / Valkey 백엔드는 third-party
서비스가 아니라 이 family 의 *자체 operator* 다.

### 1.2 본 설계가 다루는 문제

`ROADMAP.md` 에 이미 4 가지 방향이 있으나 단일 설계 정본이 없다:

1. **Forge 종속.** GitLab 전용 호출이 tool 레이어 (`forgewise/gitlab_client.py`)
   에 직접 결합돼 있다. 로드맵의 "multi-instance (GitLab + GitHub + Bitbucket)"
   를 위해 중립 seam 이 먼저 필요하다.
2. **공급망 surface 부재.** 빌드된 image 의 scan / signature 상태를 프로토콜
   안에서 보고할 방법이 없다. 로드맵: "SLSA L3 (cosign keyless)".
3. **지식 비이식성.** 결정론적 분석 결과가 호출마다 반환되고 사라진다 — 어떤
   벤더 중립·LLM 무관 포맷으로도 표현되지 않는다.
4. **장기작업 / 영속 실행 부재.** 순수 MCP 호출은 동기·단발이라 20 분~수시간
   작업을 호출 안에 들고 있을 수 없고, 크래시나 작업 도중 LLM 교체에도 아무것도
   살아남지 않는다.

### 1.3 설계 명제 — 이중 벤더 중립

상태는 LLM 세션이 아니라 **git + OKF** 에 둔다.

- **MCP** 가 *에이전트가 어떻게 호출하는가* (인터페이스) 를 정의한다.
- **OKF** (Open Knowledge Format) 가 *그 컨텍스트를 어떤 포맷으로 표현하는가*
  (지식) 를 정의한다. OKF 는 Google Cloud 의 벤더 중립 명세로, Markdown +
  YAML frontmatter 이며 `type` 만 필수다.

둘을 결합하면 인터페이스도 지식도 단일 LLM 에 종속되지 않는다. 에이전트는
**무상태 워커** 가 되고 지식 베이스가 **위키** 가 된다. 한 run 을 Claude 에서
시작해 Grok 이나 Codex 에서 같은 번들을 읽어 이어갈 수 있다.

## 2. 목표 (Goals) + 비목표 (Non-Goals)

### 2.1 Goals

| ID | 목표 | 검증 |
|---|---|---|
| G1 | `ForgeProvider` seam 도입 — GitLab 을 첫 provider, Forgejo 를 두 번째로. 33 개 public tool 시그니처는 **무변경** | 33 tool 이 provider 를 통해 해석됨 + 기존 테스트 green + `ForgeProvider` 계약 테스트 통과 |
| G2 | **read-only Harbor surface** (image 상태, Trivy scan 결과, cosign/notation 서명 검증) 를 optional tool 로 추가 | 미설정 시 graceful degradation + 기본 read-only |
| G3 | 결정론적 분석을 OKF 번들로 방출/소비하는 **OKF 지식 레이어** 추가 (Forgejo git 호스팅) | `code_review` / `vulnerability_explanation` 결과가 유효한 OKF 번들로 왕복 |
| G4 | MCP Tasks + Valkey/MongoDB 로 재개·취소 가능한 **영속 장기작업** 추가 | run 이 워커 재시작에도 생존 + 재생 시 완료 스텝 skip |
| G5 | 기존 불변식 (transport, mutation gate, audit, local gate, 오프라인-결정론 기본) 전부 보존 | `make check` 회귀 0 + `FORGEWISE_ENABLE_MUTATIONS` gate 무변경 |

### 2.2 Non-Goals

- **기존 tool 재작성.** 33 개 tool 이름·스키마·동작은 불변식이다. 본 설계는
  *가산적* — 그 아래에 seam 과 신규 optional surface 만 끼운다.
- **외부 의존성 강제.** stdio / single-user 모드는 표준 라이브러리 코어로 오늘과
  동일하게 동작해야 한다. Valkey/MongoDB/Harbor 는 **서버 모드에서만** 붙는다
  (graceful degradation).
- **GitHub Actions 추가.** RFC-0002 영구 금지 그대로. `tests/test_governance.py`
  는 `.github/workflows/` 가 생기면 계속 FAIL.
- **기본값으로 Harbor / forge 상태 변경.** 변경성 op 는 기존
  `FORGEWISE_ENABLE_MUTATIONS=1` gate 뒤에 둔다. Harbor surface 는 read-only 우선.
- **지금 GitHub / Bitbucket provider 구현.** 본 spec 은 seam + GitLab + Forgejo
  까지. 추가 provider 는 후속.

## 3. 아키텍처

```
사용자 / AI 클라이언트 (Claude · Grok · Codex — 상호 교체 가능)
  ├─ CLI: forgewise
  ├─ MCP stdio: forgewise-mcp
  └─ MCP HTTP: forgewise-http  /api/v4/mcp   (+ MCP Tasks handle)
          │
          ▼
ForgeWise tool 레이어 (33 tool — 이름/스키마 무변경)            ← 불변식
          │
   ┌──────┼───────────────┬────────────────────┐
   ▼      ▼               ▼                    ▼
ForgeProvider     Harbor surface        OKF 지식             영속 run
(seam)            (read-only 우선)      (방출 / 소비)        (MCP Tasks)
   │                    │                    │                    │
   ├─ GitLabProvider    ├─ image 상태        ├─ 번들 writer       ├─ task handle
   │  (gitlab_client)   ├─ Trivy scan        │  (md + YAML fm)    ├─ poll / 재개 / 취소
   └─ ForgejoProvider   └─ cosign verify     └─ index.md/log.md   └─ 워커 (저널)
          │                                        │                    │
          ▼                                        ▼                    ▼
   forge REST API                         Forgejo git (SSOT)    Valkey Streams + MongoDB
                                          + MongoDB 미러        (keiailab operator)

기본 (stdio / single-user): 표준 라이브러리 코어, 오프라인, 결정론적.            ← 불변식
서버 모드: 영속 백엔드 부착. audit (.forgewise/audit.jsonl) 는 항상 동작.        ← 불변식
```

**가산 원칙.** 각 신규 블록은 무변경 tool 레이어 *아래* 에 매달린다. 넷을 모두
제거하면 ForgeWise 는 오늘 v0.x 와 정확히 동일하게 동작한다.

## 4. 상세 설계

### 4.1 Forge 중립 provider (`ForgeProvider`)

현재 GitLab REST 호출은 `forgewise/gitlab_client.py` 를 통해 tool 레이어에
결합돼 있다. 33 tool 이 의존하는 forge 연산 (issue, merge/pull request, MR
commit/diff, pipeline/job, work-item note, search) 을 포착하는 `ForgeProvider`
protocol 을 도입한다. tool 함수는 *활성 provider* 를 호출하고, 구체 client 를
직접 부르지 않는다.

- `GitLabProvider` — 기존 `gitlab_client.py` 를 감싼다. 동작 보존 (기본값이라
  현 사용자에게 변화 없음).
- `ForgejoProvider` — 동일 연산을 Forgejo API (issue, PR, Forgejo Actions, 내장
  OCI/package 레지스트리) 에 매핑.
- 선택은 config/env (예: `FORGEWISE_FORGE=gitlab|forgejo`), 프로세스당 활성
  provider 1 개.

불변식: 33 tool 의 **이름과 JSON input schema 는 무변경**. provider 는 내부
seam 이고 `tools/list` 출력은 동일하다. 이것이 로드맵의 "multi-instance
(GitLab + GitHub + Bitbucket)" 를 GitLab + Forgejo 두 구현으로 실현한다.

### 4.2 Harbor surface (read-only 우선)

Forgejo 내장 레지스트리는 저장/전달 (OCI push/pull, Helm) 은 하지만 공급망 보안
(Trivy scan, cosign/notation 서명, replication, pull-through cache) 은 못 한다.
그 surface 는 Harbor 의 몫이다. 변경이 아니라 *보고* 하는 **read-only** tool 을
추가한다:

- `harbor_image_status` — repository/tag 존재, digest, push 시각, 크기.
- `harbor_scan_report` — tag 의 Trivy 취약점 요약 (severity, CVE 목록).
- `harbor_signature_verify` — cosign / notation 서명 존재 + 검증 결과.

이들은 **optional** 이다 — Harbor 미설정 시 graceful 하게 degrade 한다 (명확한
"미설정" 결과, 하드 크래시 없음). 오프라인-결정론 기본과 정합한다. 향후 변경성
op (예: tag 보존) 는 `FORGEWISE_ENABLE_MUTATIONS=1` 뒤에 둔다. 프로토콜에 서명
검증 surface 를 제공함으로써 로드맵의 "SLSA L3 (cosign keyless)" 를 전진시킨다.

### 4.3 OKF 지식 레이어

ForgeWise 가 이미 만드는 결정론적 분석 (`code_review`,
`vulnerability_explanation`, `sdlc_trends`, `root_cause_analysis`, MR 요약 …)
을 **OKF 번들** (Markdown + YAML frontmatter, `type` 만 필수) 로 방출하고, 다시
컨텍스트로 소비한다.

프로젝트 관리 지식은 OKF 개념 파일로 표현한다:

| `type` | 표현 대상 |
|---|---|
| `Project` | repository / 이니셔티브 루트 |
| `Milestone` | 전달 경계 |
| `Issue` | 작업 단위 |
| `Run` | 장기 실행 (§5 참조) |
| `Finding` | 보안 / 리뷰 결과 (분석 tool 산출) |
| `Runbook` | 운영 절차 |

`index.md` 와 `log.md` 가 개념을 상호링크해서, 같은 번들이 **보드**
(Project/Issue), **타임라인** (`log.md` + Run), **지식 그래프** (상호링크) 로
렌더된다. 번들은 Forgejo git 에 호스팅돼 (버전·diff) 단일 진실원천 (SSOT) 이
되고, 질의용으로 MongoDB 에 미러된다. 포맷이 벤더 중립이라 지식은 재인코딩 없이
Claude / Grok / Codex 간 이식된다.

### 4.4 영속 장기작업

순수 MCP 호출은 동기라 수시간 작업을 들고 있을 수 없다. 두 레이어가 해결한다:

**프로토콜 — MCP Tasks (SEP-1391).** Tasks 확장 (2026 spec RC) 은 blocking 대신
**durable handle** 을 반환한다 — 클라이언트는 폴링하고, 끊었다 재접속해 재개하고,
취소할 수 있다. 즉 장기작업이 *MCP 표준 안에서* 처리되며 기존 `forgewise-http`
transport 로 노출된다.

**실행 — durable 워커.** 실제 워크플로는 durable execution 워커 (Valkey Streams +
워커; Temporal / Restate / DBOS 도 대안) 로 돈다. 엔진은 **이벤트 저널 기반**
이라 크래시 후 완료 스텝을 건너뛰고 재개한다. 비결정적 LLM 호출은 결과가
저널되는 **activity** 로 감싸므로, 재생 시 모델을 다시 부르지 않고 기록된 출력을
재사용한다.

필수 정합성 장치 (at-least-once 보정):

- **멱등키** `(run_id + step_id)` — 재생된 스텝은 no-op.
- **MongoDB outbox** — 상태 변경과 방출 effect 가 원자적으로 commit.
- **Valkey lease** — 두 워커가 같은 스텝을 돌리는 것을 방지.
- **리컨실리에이션 루프** — 부분 실패 후 의도한 상태 ↔ 실제 상태 수렴.

keiailab `valkey-operator` (Streams/lease/cache) 와 `mongodb-operator`
(outbox/문서 저장) 가 뒷받침한다. stdio / single-user 모드에는 이들이 없고 tool
은 오늘처럼 동기로 동작한다.

## 5. 영속성 + 연속성

| 관심사 | 메커니즘 | 진실원천 |
|---|---|---|
| 영속성 | Forgejo git 의 OKF 번들 (버전 + diff + `log.md`) + MongoDB 미러 | **Forgejo git** — 전 인프라가 죽어도 `git clone` 으로 복원 |
| 캐시 / 큐 | Valkey (Streams, lease, cache) | 휘발성 — 1차 소스 아님 |
| 연속성 | `type: Run` + `log.md` + 체크포인트 | 번들 — 어떤 에이전트든 읽어서 재개 |
| LLM 독립 | OKF (지식) + MCP (인터페이스) | 어느 쪽도 모델에 종속 안 됨 |

"에이전트 = 무상태 워커, 지식 = 위키" 패턴이라, 세션이 끝나거나 작업 도중
Claude → Grok 으로 바꿔도 진행이 사라지지 않는다 — 다음 에이전트가 번들을 읽고
마지막 체크포인트부터 잇는다.

## 6. 리스크 + 완화

| 리스크 | 영향 | 완화 |
|---|---|---|
| provider seam 으로 GitLab-ism 이 tool 에 샘 | Forgejo provider 가 계약 충족 불가 | `ForgeProvider` 계약을 GitLab API 가 아니라 *tool 필요* 에서 정의 + 두 provider 모두에 계약 테스트 |
| MCP Tasks (SEP-1391) 아직 RC | GA 전 spec 변동 가능 | durable 워커를 seam 뒤에 둠 + Tasks 는 `forgewise-http` 에만 노출 + 미지원 시 동기로 degrade |
| at-least-once 이중 effect | 부수효과 중복 | 멱등키 + MongoDB outbox + Valkey lease (선택 아닌 필수) |
| 신규 optional dep (Harbor/Valkey/Mongo) 가 코어로 침투 | 오프라인-결정론 기본 파괴 | 하드 규칙: stdio/single-user 는 서버 dep 미import + 서버 백엔드는 config 뒤 lazy-load |
| OKF 스키마가 upstream 과 drift | 번들 검증 실패 | OKF v0.1 핀 + `type` 만 필수 + 방출 시 검증 |

## 7. 성공 기준 (Success Criteria)

```
# 1. 33 tool 전부 ForgeProvider 통해 해석; 이름/스키마 무변경
# 2. ForgejoProvider 가 GitLabProvider 와 동일 계약 테스트 통과
# 3. Harbor 미설정 시 Harbor tool 이 graceful "미설정" 결과 반환
# 4. code_review 결과가 유효한 OKF v0.1 번들로 왕복
# 5. 영속 run 이 워커 재시작 생존 + 재생 시 완료 스텝 skip
# 6. make check 회귀 0 + FORGEWISE_ENABLE_MUTATIONS gate 무변경
# 7. stdio/single-user 모드가 Valkey/Mongo/Harbor/FastAPI 서버 dep 미import
# 8. .github/workflows/ 출현 시 tests/test_governance.py 여전히 FAIL
```

## 8. 본 spec 의 out-of-scope (별 sub-project)

- GitHub / Bitbucket provider (본 spec 은 seam + GitLab + Forgejo 까지).
- Harbor *변경성* op (retention, GC) — read-only 우선.
- 특정 durable 엔진 선택 (Temporal vs Valkey-native) — pluggable.
- OKF 렌더링 UI (보드/타임라인/그래프 뷰어) — 본 spec 은 데이터를 정의, 뷰어는 별도.

## 9. 다음 단계

1. `ForgeProvider` seam 착수 (`gitlab_client.py` 를 그 뒤로 리팩터, tool 무변경)
   — 가장 작고 레버리지 큰 첫 스텝.
2. `ForgejoProvider` + 계약 테스트 추가.
3. read-only Harbor surface (tool 3 종).
4. 기존 분석 tool 의 OKF emitter + 번들 왕복 테스트.
5. durable 워커 (Valkey Streams) + `forgewise-http` 에 MCP Tasks handle.
6. `ROADMAP.md` / `README.md` 에 본 spec 링크 + ja/zh 번역 추가.

## 부록 A. 정의 (Definitions)

- **OKF (Open Knowledge Format)** — 벤더 중립 지식 포맷 (Markdown + YAML
  frontmatter, `type` 만 필수).
- **MCP Tasks** — 장기작업용 durable task handle 을 반환하는 MCP 확장
  (SEP-1391, poll / 재개 / 취소).
- **ForgeProvider** — forge 연산을 추상화해 tool 을 forge 중립으로 만드는 내부 seam.
- **Outbox** — 상태 변경과 방출 effect 를 원자적으로 commit 해 effect 의
  유실/중복을 막는 패턴.
- **Lease** — 중복 워커를 막는 단기 배타 점유 (Valkey).

## 부록 B. 참조

- [OKF v0.1 spec — GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [MCP Tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview)
- [SEP-1391: Long-Running Operations (MCP)](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1391)
- [Durable Execution Patterns for AI Agents (Zylos Research)](https://zylos.ai/research/2026-02-17-durable-execution-ai-agents)
- [Harbor — enterprise-grade container registry (CNCF)](https://www.cncf.io/blog/2025/12/08/harbor-enterprise-grade-container-registry-for-modern-private-cloud/)
- [Forgejo Container Registry](https://forgejo.org/docs/latest/user/packages/container/)
- 레포: `docs/design.md`, `ROADMAP.md`, `docs/configuration.md`, `docs/family.md`
