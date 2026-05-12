# ForgeWise 레퍼런스

작성일: 2026-05-12

## GitLab Duo 기능 기준

- GitLab Duo 공식 기능표:
  https://docs.gitlab.com/user/gitlab_duo/feature_summary/

이 문서에서 확인한 Enterprise 기능군은 Code Suggestions, Chat, Code Explanation,
Refactor Code, Fix Code, Test Generation, Code Review, Root Cause Analysis,
Vulnerability Explanation, Vulnerability Resolution, SDLC trends, Merge Commit
Message Generation, MR/Code Review/Issue Description summary 계열입니다.

ForgeWise는 이 기능군을 코드 forge 독립 CLI/MCP tool로 매핑합니다. 상표나 UI를
복제하지 않고 기능 계약만 오픈소스로 재구성합니다.

## MCP 기준

- MCP tools spec:
  https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- MCP authorization spec:
  https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization

반영한 설계 포인트:

- tool result는 text content와 structured content를 함께 줄 수 있습니다.
- tool에는 input schema를 제공해야 LLM과 클라이언트가 안정적으로 호출할 수 있습니다.
- 서버는 입력 검증, access control, rate limit, output sanitization, audit logging을
  고려해야 합니다. MVP는 입력 경로 제한, 비밀값 마스킹, audit log부터 구현합니다.
- stdio transport는 환경변수 기반 자격증명을 쓰는 방향이 권장되므로, MVP는 HTTP auth를
  구현하지 않습니다.

## 참고한 오픈소스 프로젝트

- Tabby: https://github.com/TabbyML/tabby
  - self-hosted AI coding assistant, GitLab/GitHub integration, admin/analytics 방향 참고
- Continue: https://github.com/continuedev/continue
  - source-controlled AI checks와 repository-local check 정의 방식 참고
- Aider: https://github.com/Aider-AI/aider
  - 터미널 기반 pair programming, codebase map, git-aware workflow 참고
- OpenHands: https://github.com/OpenHands/OpenHands
  - CLI, SDK, local GUI, enterprise self-hosting 경계와 권한/RBAC 방향 참고

## ForgeWise가 바로 가져오지 않은 것

- IDE extension completion loop
- 외부 LLM agent loop
- cloud multi-tenant admin UI
- 실시간 MR comment writer

이 네 가지는 보안과 운영 경계가 크기 때문에, 로컬 deterministic MCP tool 표면을
먼저 안정화한 뒤 별도 milestone로 추가합니다.
