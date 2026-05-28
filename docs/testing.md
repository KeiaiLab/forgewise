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


## E2E Tests with Real GitLab CE

End-to-end tests run against a real GitLab CE instance started via Docker Compose.
They are **excluded** from `make check` and only run when `FORGEWISE_E2E=1` is set.

### Prerequisites

- Docker and Docker Compose installed
- Port 9080 available on localhost

### 1. Start GitLab CE

```bash
docker compose -f docker-compose.e2e.yml up -d
```

First boot takes **3-5 minutes**. Wait for the health check to pass:

```bash
docker compose -f docker-compose.e2e.yml ps
# STATUS should show "healthy"
```

### 2. Seed Test Data

Once GitLab CE is healthy, run the seed script to create a test project, issue,
and personal access token:

```bash
docker compose -f docker-compose.e2e.yml exec gitlab bash /opt/gitlab-e2e-seed.sh
```

This creates:
- A Personal Access Token: `e2e-test-token`
- A project: `root/forgewise-e2e-test`
- A test issue and a source file (`src/hello.py`) for blob search tests

### 3. Run E2E Tests

```bash
FORGEWISE_E2E=1 \
GITLAB_TOKEN=e2e-test-token \
GITLAB_BASE_URL=http://localhost:9080 \
FORGEWISE_ENABLE_MUTATIONS=1 \
  uv run --extra dev python -m pytest tests/test_e2e_gitlab.py -v
```

| Variable | Description | Default |
|---|---|---|
| `FORGEWISE_E2E` | Set to `1` to enable E2E tests | (skip) |
| `GITLAB_TOKEN` | GitLab API token | (required) |
| `GITLAB_BASE_URL` | GitLab CE base URL | `http://localhost:9080` |
| `FORGEWISE_E2E_PROJECT_ID` | Test project path | `root/forgewise-e2e-test` |
| `FORGEWISE_ENABLE_MUTATIONS` | Allow mutation tools (create_issue, etc.) | (required for write tests) |

### 4. Teardown

```bash
docker compose -f docker-compose.e2e.yml down -v
```

The `-v` flag removes volumes to free disk space.

### Test Coverage

The E2E suite verifies at least these GitLab-compatible tool flows:

1. **search (projects scope)** -- list projects via search API
2. **search_labels** -- confirm project access via label listing
3. **search (issues scope)** -- search issues within a project
4. **create_issue + get_issue** -- create an issue, then fetch it
5. **search (blobs scope)** -- search code within a project
6. **server_version** -- verify MCP server metadata
7. **create_workitem_note + get_workitem_notes** -- note creation and listing

### Notes

- E2E tests use `@pytest.mark.e2e` marker, registered in `pyproject.toml`.
- All fixtures use `scope="session"` to minimize GitLab API calls.
- No GitHub Actions are used (RFC-0002). Run E2E tests locally only.
