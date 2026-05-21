# Installation

> **English** | [한국어](installation.ko.md) | [日本語](installation.ja.md) | [中文](installation.zh.md)

ForgeWise 는 Python 3.11+ 기반 MCP-native developer intelligence 서버다. 본 문서는
설치 / 환경 설정 / 검증 / 트러블슈팅을 다룬다.

## 시스템 요구

| 항목 | 최소 | 권장 |
|---|---|---|
| Python | 3.11 | 3.11 또는 3.12 |
| `uv` | 0.4 | 0.5+ |
| 디스크 | 50 MB | 200 MB (개발 + 캐시) |
| OS | Linux / macOS | Linux x86_64 (운영) |
| Memory | 256 MB | 1 GB (대규모 저장소 분석 시) |

`pip` 단독 환경도 지원하지만 `uv` 가 권장된다 (lockfile 일관성, 빌드 속도).

## 빠른 설치

### Option 1 — `uv` (권장)

개발용 (저장소 clone):

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
uv sync --extra dev
```

배포용 (PyPI 게시 후, 현재 unreleased):

```bash
uv tool install forgewise
```

### Option 2 — `pip`

개발용:

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

배포용 (PyPI 게시 후):

```bash
pip install forgewise
```

## 환경 변수

ForgeWise 의 런타임 동작은 다음 환경 변수로 제어한다. **별표 (*)** 는 운영 환경 필수.

| 변수 | 필수? | 기본값 | 설명 |
|---|---|---|---|
| `GITLAB_BASE_URL` | * | `https://gitlab.com` | GitLab CE/EE 인스턴스 URL (예: `https://gitlab.example.com`) |
| `GITLAB_TOKEN` | * | (없음) | GitLab API token (Personal Access Token 또는 Project Access Token) |
| `FORGEWISE_ENABLE_MUTATIONS` | no | (미설정) | `1` 로 설정 시 변경성 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`) 허용. 미설정 시 차단. |
| `FORGEWISE_REQUIRE_OAUTH` | no | (미설정) | HTTP transport 에서 OAuth 2.0 인증 강제. 운영 환경에서는 `1` 권장. |
| `FORGEWISE_LIVE_GITLAB_TOKEN` | no | (없음) | `make smoke-gitlab` 용 별도 token (테스트 환경 격리) |
| `FORGEWISE_LIVE_PROJECT_ID` | no | (없음) | `make smoke-gitlab` 의 테스트 대상 project ID 또는 full path |

### OAuth 2.0 응용 변수 (HTTP transport)

| 변수 | 필수? | 설명 |
|---|---|---|
| `FORGEWISE_OAUTH_CLIENT_ID` | yes (HTTP + OAuth) | OAuth 2.0 client ID (Dynamic Client Registration 사용 시 자동 발급) |
| `FORGEWISE_OAUTH_CLIENT_SECRET` | yes (HTTP + OAuth) | OAuth 2.0 client secret. `.env` 또는 secret manager 로 주입. **commit 절대 금지.** |
| `FORGEWISE_LOG_LEVEL` | no | `DEBUG` / `INFO` (기본) / `WARN` / `ERROR` |

### `.env` 양식 예시

```bash
# .env (절대 commit 금지 — .gitignore 포함)
GITLAB_BASE_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
FORGEWISE_ENABLE_MUTATIONS=
FORGEWISE_REQUIRE_OAUTH=1
FORGEWISE_OAUTH_CLIENT_ID=forgewise-prod
FORGEWISE_OAUTH_CLIENT_SECRET=...
FORGEWISE_LOG_LEVEL=INFO
```

## 검증

설치 직후 다음 명령으로 환경을 검증한다:

```bash
# 1. CLI 동작 확인
forgewise --version
forgewise --repo . check

# 2. MCP stdio transport 시작 (Ctrl+C 로 종료)
forgewise-mcp

# 3. MCP HTTP transport 시작 (별 shell, Ctrl+C 로 종료)
forgewise-http --host 127.0.0.1 --port 8080

# 4. 로컬 게이트 (개발 환경)
make check

# 5. GitLab live smoke (선택, GITLAB_TOKEN + FORGEWISE_LIVE_PROJECT_ID 필요)
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise make smoke-gitlab
```

모두 zero exit code 시 환경 정상. `make check` 가 ruff + mypy + pytest 543 LOC 를
검증한다.

## 트러블슈팅

### OAuth 인증 실패

증상: HTTP transport `/api/v4/mcp` 호출 시 `401 Unauthorized`.

원인 / 대응:

1. `FORGEWISE_REQUIRE_OAUTH=1` 이지만 client 가 token 미전달 → `Authorization:
   Bearer <access_token>` header 확인.
2. token 만료 (기본 1 시간) → `/oauth/token` 재요청.
3. redirect URI 미허용 → `https://` / `127.0.0.1` / `localhost` 만 허용. 다른
   스킴은 client 등록 자체가 거부됨.
4. PKCE code_verifier 불일치 → `S256` 인 경우 base64url(SHA-256(verifier)) 검증
   확인.

상세는 `docs/security.md` 의 OAuth 섹션 참조.

### GitLab 연결 실패

증상: `GitLab API 호출 실패: HTTP 401` 또는 `Connection refused`.

원인 / 대응:

1. `GITLAB_TOKEN` 미설정 → `.env` 확인 + `source .env` 또는 process manager 의
   env 주입 확인.
2. token 권한 부족 → `read_repository` + `read_api` 최소. 변경성 tool 사용 시
   `api` scope 필요.
3. `GITLAB_BASE_URL` 오타 → `https://` 포함, trailing slash 없음 권장.
4. self-signed cert → `httpx` 의 `verify=False` 우회는 **금지**. 사내 CA chain 을
   시스템 trust store 에 등록.
5. network proxy → `HTTPS_PROXY` / `HTTP_PROXY` 환경 변수 정상 설정 확인.

### Python 버전 불일치

증상: `python: command not found` 또는 `Python 3.10 detected, requires >= 3.11`.

대응:

```bash
# uv 사용 시 자동 분리된 Python
uv python install 3.11

# 또는 pyenv
pyenv install 3.11.10
pyenv local 3.11.10
```

`Makefile` 의 `PYTHON ?= 3.11` override 가능: `make check PYTHON=3.12`.

### mypy strict 실패

증상: `make check` 의 typecheck 단계에서 `Function is missing a type annotation`.

대응: `pyproject.toml` 의 `[tool.mypy] strict = true` + `disallow_untyped_defs =
true` 가 SSOT. 신규 코드는 모든 함수 signature 에 type annotation 의무.
`# type: ignore[<code>]` 우회는 PR body 에 사유 명시.

### lefthook hook 비활성

증상: `git commit` 시 hook 출력 0.

대응:

```bash
# hook 설치 확인
ls -la .git/hooks/pre-commit .git/hooks/pre-push .git/hooks/commit-msg

# 미설치 시
make setup-hooks
```

`LEFTHOOK=0 git commit ...` 으로 전체 우회 가능하지만 PR 본문에 사유 명시 의무.

## 다음 단계

- 환경 설정 상세: `docs/configuration.md`
- 33 종 MCP tool 카탈로그: `docs/api-reference.md`
- 버전 마이그레이션: `docs/upgrade.md`
- 보안 정책: `docs/security.md` + `SECURITY.md`
- 기여 가이드: `CONTRIBUTING.md`
