# Upgrade Guide

> **English** | [한국어](upgrade.ko.md) | [日本語](upgrade.ja.md) | [中文](upgrade.zh.md)

ForgeWise 의 버전 마이그레이션 가이드. SemVer 정책 + 향후 버전 호환성.

## SemVer 정책

ForgeWise 는 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) 을
따른다.

| 단계 | 정책 |
|---|---|
| `0.x.y` (alpha — 현재) | minor (`y` → `y+1`) 도 breaking change 가능. 모든 breaking change 는 `CHANGELOG.md` 의 `### Changed` 또는 `### Removed` 섹션 + 본 문서 마이그레이션 가이드 추가. |
| `1.0.0` 이후 | 엄격 SemVer. MAJOR = breaking, MINOR = additive, PATCH = bug fix. |

## 현재 버전

| Stream | 버전 | 상태 |
|---|---|---|
| `main` | `0.1.0` + Unreleased | 활성 |

`CHANGELOG.md` 의 `[Unreleased]` 섹션이 다음 릴리스 후보 변경점의 SSOT.

## 마이그레이션 가이드

### vN/A → v0.1.0 (initial release)

**현재 initial release 준비 중**. 별도 마이그레이션 단계 없음.

설치는 `docs/installation.md` 참조.

#### OAuth 토큰 해싱 전환 (#28)

**Breaking change (DB 비호환)**: OAuth SQLite DB 의 `access_token`, `client_secret`,
`registration_access_token` 이 SHA-256 해시로 저장됩니다. 기존 평문 저장 DB 와
호환되지 않습니다.

**마이그레이션 단계:**

1. 기존 OAuth DB 파일 삭제 (기본 경로: `oauth_store_path` 설정값)
2. 서버 재시작 — 새 DB 가 자동 생성됩니다
3. 기존 클라이언트는 재등록 (DCR) 필요

**영향:**
- 기존에 발급된 모든 access_token 이 무효화됩니다
- 기존에 등록된 모든 client 의 client_secret 이 무효화됩니다
- 신규 발급 토큰부터 해시 저장이 적용됩니다

> 이 변경은 DB 유출 시 토큰 평문 노출 위험을 제거합니다.

### v0.1.0 → v0.2.0 (placeholder)

(향후 v0.2.0 release 시점에 작성. 양식 예시:)

#### Breaking changes

(예시)
- `forgewise.policy.json` 조직 정책 파일 도입 — 미존재 시 기본 정책 적용
- 환경 변수 `FORGEWISE_OAUTH_CLIENT_ID` 신규 필수 (HTTP transport + OAuth)
- MCP tool `<tool_name>` 의 input schema 에 `<param>` 추가 (required)

#### 마이그레이션 단계

(예시)
1. `forgewise.policy.json` 작성 (template: `docs/policy-template.json`)
2. `.env` 에 `FORGEWISE_OAUTH_CLIENT_ID` 추가
3. MCP client 의 `<tool_name>` 호출 site 에 `<param>` 추가
4. `make check` + `forgewise --repo . check` 회귀 검증

#### 환경 변수 매핑

| v0.1.0 | v0.2.0 | 비고 |
|---|---|---|
| `<old_var>` | `<new_var>` | (예시) rename — 기존 변수는 1 release 동안 deprecated alias 유지 |

#### MCP tool 이름 매핑

| v0.1.0 | v0.2.0 | 비고 |
|---|---|---|
| `<old_tool>` | `<new_tool>` | (예시) rename — alias 1 release 유지 |

### vN → vN+1 (general template)

신규 minor / major release 마다 본 섹션 추가:

```markdown
### v<old> → v<new> (<release date>)

#### Breaking changes
- ...

#### 마이그레이션 단계
1. ...

#### 환경 변수 매핑
| <old> | <new> | 비고 |

#### MCP tool 이름 매핑
| <old> | <new> | 비고 |

#### 데이터 호환성
- `.forgewise/audit.jsonl` 양식 변경 시 자동 마이그레이션 스크립트 명세
- 기타 영구 데이터 (DB, cache) 마이그레이션
```

## 의존성 갱신

`uv.lock` 은 SSOT. 의존성 갱신:

```bash
# 모든 의존성 latest compatible 로 갱신
uv sync --upgrade

# 회귀 검증
make check

# 차이 확인
git diff uv.lock pyproject.toml

# 변경 없으면 commit, 회귀 있으면 lockfile 만 restore:
# git checkout uv.lock pyproject.toml
```

major version bump 가 발생한 dependency 는 PR body 에 `<dep>: vN → vN+1` 명시.
breaking change 가 의심되는 dep (uvicorn / fastapi / authlib / httpx) 는 별 PR 로
분리하여 회귀 위험 격리.

## MCP protocol 갱신

ForgeWise 는 다음 MCP protocol version 을 협상 (`forgewise/mcp_server.py` 의
`initialize` 응답):

- `2025-03-26` (legacy)
- `2025-06-18` (current)

새 protocol spec 도입 시:

1. `forgewise/mcp_server.py` 의 `_NEGOTIATED_PROTOCOL_VERSIONS` 갱신
2. 새 spec 의 capability 차이를 본 문서에 마이그레이션 가이드 추가
3. legacy protocol 지원 deprecate / 제거 시점 명시
4. `tests/test_mcp_server.py` 의 protocol assertion 갱신

## 데이터 호환성

### `.forgewise/audit.jsonl`

JSONL append-only log. schema 변경 시:

| 변경 유형 | 호환성 | 대응 |
|---|---|---|
| 신규 field 추가 (optional) | backward compatible | 무대응 (기존 reader 가 unknown field 무시) |
| 기존 field rename | breaking | 자동 마이그레이션 스크립트 + 본 문서 가이드 |
| 기존 field 제거 | breaking | 자동 마이그레이션 스크립트 + deprecation 1 release |

자동 마이그레이션 스크립트는 `tools/migrate-audit.py` (현재 미작성, vN+1 에서
breaking change 발생 시 추가).

### `.secrets.baseline`

`detect-secrets` 의 baseline. ForgeWise 버전과 독립. tool 버전 upgrade 시:

```bash
uv tool upgrade detect-secrets
uv run detect-secrets scan --baseline .secrets.baseline
```

## 다운그레이드

ForgeWise 는 *공식적으로 다운그레이드를 지원하지 않는다*. `0.x` 동안 audit log /
secrets baseline 의 forward-only 마이그레이션만 보장.

긴급 상황 시:

1. 이전 version 으로 `pip install forgewise==<old_version>` (PyPI 게시 후)
2. `.forgewise/audit.jsonl` backup 후 신규 라인 제거 (manual)
3. issue 등록 + 다운그레이드 사유 명시

## 다음 단계

- 설치: `docs/installation.md`
- 환경 설정: `docs/configuration.md`
- API 카탈로그: `docs/api-reference.md`
- 변경 이력: `CHANGELOG.md`
