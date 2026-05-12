# ForgeWise 보안 운영 기준

작성일: 2026-05-12

## 기본 정책

- 기본 실행은 로컬 결정론적 분석이며 외부 LLM을 호출하지 않는다.
- stdio MCP와 HTTP MCP는 같은 tool registry를 사용한다.
- HTTP transport는 `/api/v4/mcp`로 노출하며, 운영 환경에서는
  `FORGEWISE_REQUIRE_OAUTH=1`을 켠다.
- GitLab 변경성 tool은 `FORGEWISE_ENABLE_MUTATIONS=1`이 없으면 실패한다.

## OAuth

ForgeWise HTTP 서버는 로컬 MCP client 연결을 위해 OAuth 2.0 Dynamic Client
Registration 형태의 `/oauth/register`, `/oauth/authorize`, `/oauth/token`을 제공한다.

- client 등록은 `https://`, `http://127.0.0.1`, `http://localhost` redirect URI만 허용한다.
- authorization code는 5분 후 만료된다.
- token은 1시간 후 만료된다.
- PKCE `plain`, `S256`을 지원한다.

## GitLab API token

GitLab REST API 호출에는 `GITLAB_TOKEN` 또는 tool argument `gitlab_token`이 필요하다.
감사 로그와 오류 메시지에는 token, secret, password, key 계열 인자를 기록하지 않는다.

## Prompt injection 경계

MCP client가 GitLab issue, MR, note, code search 결과를 다시 LLM prompt에 넣을 수 있다.
ForgeWise는 외부 텍스트를 신뢰하지 않는다.

- GitLab API 결과는 구조화 데이터로 반환하고 자동 명령 실행에 사용하지 않는다.
- 변경성 tool은 환경 변수 정책으로 별도 승인한다.
- client는 issue/MR 본문 안의 지시문을 시스템 지시보다 낮은 신뢰도로 다뤄야 한다.
