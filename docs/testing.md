# 테스트와 로컬 게이트

ForgeWise는 GitHub Actions를 쓰지 않습니다. 로컬 3개 게이트를 `Makefile`에 모읍니다.

```bash
make check
```

게이트:

- `make lint`: ruff 규칙 검증
- `make typecheck`: mypy strict 검증
- `make test`: pytest 실행

현재 테스트 범위:

- repository scanner와 라인 slice
- code explanation, local chat retrieval, test generation
- vulnerability explanation/resolution
- MCP tool list와 `tools/call` structuredContent
- Merge commit message / code review summary / issue description generation
- CLI JSON 출력과 `check` 실패 exit code
- GitHub Actions 금지와 제품 문서 존재

## 선택적 live GitLab smoke

실제 GitLab API 접근은 기본 로컬 게이트에 넣지 않습니다. 토큰이 있을 때만 별도 smoke로
실행합니다.

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... \
FORGEWISE_LIVE_PROJECT_ID=group/project \
make smoke-gitlab
```

환경 변수가 없으면 smoke는 skip으로 종료합니다. 이 smoke는 `get_mcp_server_version`과
read-only label 조회로 HTTP/API 연결성을 확인합니다.
