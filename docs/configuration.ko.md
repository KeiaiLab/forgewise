# 설정 (Configuration)

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> [English](configuration.md) | **한국어** | [日本語](configuration.ja.md) | [中文](configuration.zh.md)

ForgeWise 의 운영 인터페이스 (MCP client 등록 / OAuth scope / GitLab 인증 /
audit log / mutation gate) 를 정리한다. 환경 변수 표는 `docs/installation.md`
참조.

## MCP client 등록

ForgeWise 는 두 가지 transport 를 제공한다.

### stdio transport (`forgewise-mcp`)

로컬 MCP client (Claude Desktop, Cursor, Continue 등) 와 직접 통신. 추가 인증 불필요
(client 가 hosting OS 의 권한으로 실행).

Claude Desktop `claude_desktop_config.json` 예시:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp",
      "env": {
        "GITLAB_BASE_URL": "https://gitlab.example.com",
        "GITLAB_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Cursor `.cursor/mcp.json` 양식도 동일.

### HTTP transport (`forgewise-http`)

원격 MCP client + 다중 사용자 환경. FastAPI + uvicorn + OAuth 2.0 Dynamic Client
Registration.

```bash
forgewise-http --host 127.0.0.1 --port 8080 --require-oauth
```

CLI option:

| Option | 기본값 | 설명 |
|---|---|---|
| `--host` | `127.0.0.1` | bind address. 0.0.0.0 사용 시 firewall + reverse proxy 권장 |
| `--port` | `8080` | bind port |
| `--require-oauth` | (off) | OAuth 2.0 인증 강제. 운영 환경 권장 (`FORGEWISE_REQUIRE_OAUTH=1` 와 동등) |
| `--workers` | `1` | uvicorn worker 수 (CPU bound 가 아니므로 보통 1 충분) |

MCP endpoint: `POST /api/v4/mcp` (GitLab MCP server 호환 URL).

## MCP tool input schema 정책

모든 33 종 tool 은 JSON Schema strict mode 입니다. 일반 패턴:

```json
{
  "name": "<tool_name>",
  "description": "<한국어 설명>",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string", "description": "저장소 루트 경로. 생략 시 서버 기본 경로 사용."},
      "<param>": {"type": "<type>", "description": "<한국어 설명>"}
    },
    "required": ["<param>"]
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false
  }
}
```

`annotations.readOnlyHint`:

- `true` — 모든 read-only tool (Duo 18 종 + GitLab 조회 tool)
- `false` — 변경성 tool. `openWorldHint: true` 부가. `FORGEWISE_ENABLE_MUTATIONS=1`
  필요.

상세 tool 별 schema 는 `docs/api-reference.md` 참조.

## OAuth 2.0 scope

ForgeWise 의 GitLab OAuth 2.0 application 에 등록할 scope:

| Scope | 용도 | 필수? |
|---|---|---|
| `read_repository` | 코드 분석 (read-only). git clone / file read 동등. | yes |
| `read_api` | GitLab API 조회 (issue / MR / pipeline / search). | yes |
| `api` (write) | 변경성 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`). | **선택** — `FORGEWISE_ENABLE_MUTATIONS=1` 시에만 필요. 운영 환경에서는 별도 OAuth application 분리 권장. |

### DCR endpoint

| Endpoint | Method | 용도 |
|---|---|---|
| `/oauth/register` | POST | Dynamic Client Registration. redirect URI 등록. |
| `/oauth/authorize` | GET | Authorization code 발급 (5 분 만료) |
| `/oauth/token` | POST | Access token 교환 (1 시간 만료) |
| `/oauth/.well-known/oauth-authorization-server` | GET | RFC 8414 metadata |

PKCE: `plain` / `S256` 지원. `S256` 권장.

Redirect URI 허용 패턴:

- `https://*` (TLS 강제)
- `http://127.0.0.1:*` (localhost dev)
- `http://localhost:*` (localhost dev)

다른 스킴은 client 등록 자체 거부.

## GitLab API 인증

GitLab REST API 호출에는 token 이 필요하다. ForgeWise 는 다음 우선순위로 token 을
resolve:

1. **Tool argument** `gitlab_token` (per-call override)
2. **환경 변수** `GITLAB_TOKEN` (서버 시작 시)
3. (없음) → tool 실패: `필수 인자가 없습니다: gitlab_token`

마스킹 정책: token 은 절대 audit log 에 기록되지 않는다. 비밀값 키워드 (`token` /
`secret` / `password` / `key`) 가 포함된 argument 는 `[REDACTED]` 로 자동 마스킹.

## audit log

ForgeWise 는 모든 tool 호출을 `.forgewise/audit.jsonl` 에 기록한다.

### 위치

```
<repo_root>/.forgewise/audit.jsonl
```

각 줄 = 1 JSON object (JSONL). 양식:

```json
{
  "ts": "2026-05-21T10:30:00.000000Z",
  "tool": "code_review",
  "arguments": {"repo": ".", "gitlab_token": "[REDACTED]"},
  "result_summary": {"finding_count": 7, "severity_high": 2}
}
```

### 마스킹 규칙

다음 키워드를 포함한 argument key 는 value 가 `[REDACTED]` 로 자동 치환:

- `token` (예: `gitlab_token`)
- `secret` (예: `client_secret`)
- `password`
- `key` (예: `api_key`)

상세: `forgewise/audit.py:mask_secrets` 참조.

### 로테이션

ForgeWise 는 audit log 자동 rotation 을 제공하지 않는다. logrotate 또는 cron job 으로
주기적 archive 권장 (예: 주 1회, gzip 압축).

## mutation gate

`FORGEWISE_ENABLE_MUTATIONS=1` 미설정 시 다음 tool 이 호출 차단:

| Tool | 영향 |
|---|---|
| `create_issue` | GitLab issue 신규 생성 |
| `create_merge_request` | GitLab MR 신규 생성 |
| `manage_pipeline` (`operation != list`) | pipeline create / retry / cancel |
| `create_workitem_note` | Work item note 신규 |

차단 시 error message: `변경성 GitLab tool은 FORGEWISE_ENABLE_MUTATIONS=1일 때만
실행됩니다.`

운영 환경에서는 *읽기 전용* MCP application 과 *쓰기 가능* MCP application 을 분리
배포하고, OAuth scope + `FORGEWISE_ENABLE_MUTATIONS` 환경 변수를 별도 관리 권장.

## smoke-gitlab 활용

`make smoke-gitlab` 은 live GitLab 인스턴스에 대해 read-only tool subset 을 호출하여
연결성 + 권한을 검증한다. CI 부재 환경의 *제 4 계층 (수동 게이트)*.

```bash
export FORGEWISE_LIVE_GITLAB_TOKEN=glpat-xxx
export FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise
make smoke-gitlab
```

출력 예시:

```
== ForgeWise GitLab smoke test ==
[1/5] get_mcp_server_version ... OK (version: 0.1.0)
[2/5] get_issue (#1) ... OK
[3/5] search (scope=blobs, search='ForgeWise') ... OK (5 hits)
[4/5] search_labels ... OK (12 labels)
[5/5] get_merge_request_commits (!1) ... OK (3 commits)
PASS
```

변경성 tool 은 smoke 에 포함되지 않음 (운영 환경 부수 효과 회피).

## 분석 결과 — tool 카운트

ForgeWise 0.1.0 은 총 **33 종 MCP tool** 을 제공:

- **18 종 GitLab Duo Enterprise 대응** (모두 local, 외부 LLM 미호출)
- **15 종 GitLab MCP compatible** (GitLab API proxy)

상세 카탈로그는 `docs/api-reference.md` 참조.

## 다음 단계

- 설치: `docs/installation.md`
- API 카탈로그: `docs/api-reference.md`
- 버전 마이그레이션: `docs/upgrade.md`
- 보안 정책: `docs/security.md` + `SECURITY.md`
