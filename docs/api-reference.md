# API Reference — MCP tools

> **English** | [한국어](api-reference.ko.md) | [日本語](api-reference.ja.md) | [中文](api-reference.zh.md)

ForgeWise 0.1.0 의 33 종 MCP tool 카탈로그. 모든 정보는 `forgewise/tools.py` 의
`list_tool_definitions()` 가 SSOT. 본 문서는 *문서화 사본* 으로, 신규 tool 추가 /
schema 변경 시 본 문서 + `tests/test_mcp_server.py` + `docs/design.md` 동시 갱신
의무 (CONTRIBUTING.md "Adding a New MCP Tool" 정책).

## 공통 사항

### 입력 schema 공통 property

| Property | Type | Required | 설명 |
|---|---|---|---|
| `repo` | string | optional | 저장소 루트 경로. 생략 시 서버 기본 경로 사용. 단 `get_mcp_server_version` 등 일부 tool 은 `accepts_repo: false` |

### GitLab compat tool 추가 공통 property

GitLab API 를 호출하는 모든 tool 의 input schema 에 다음 공통 property 가 포함된다:

| Property | Type | Required | 설명 |
|---|---|---|---|
| `gitlab_base_url` | string | optional | GitLab base URL. 기본값 = `GITLAB_BASE_URL` 환경 변수 또는 `https://gitlab.com` |
| `gitlab_token` | string | optional | GitLab API token. 기본값 = `GITLAB_TOKEN` 환경 변수 |
| `gitlab_timeout` | number | optional | GitLab API timeout (초) |

### 출력 양식

모든 tool 의 응답은 MCP 표준:

```json
{
  "content": [
    {"type": "text", "text": "<JSON string of structured data>"}
  ],
  "structuredContent": {<same JSON as above>}
}
```

`structuredContent` 는 tool 별로 schema 가 다름. 본 문서의 각 tool entry 의 "output"
섹션 참조.

### Annotations

| Annotation | 의미 |
|---|---|
| `readOnlyHint: true` | tool 호출이 외부 상태를 변경하지 않음 |
| `readOnlyHint: false` | 변경성 tool. `FORGEWISE_ENABLE_MUTATIONS=1` 필요 |
| `destructiveHint: false` | 명시적으로 비파괴적 |
| `openWorldHint: true` | 외부 시스템 (GitLab) 의 상태 변경 가능 |

---

## Category A — GitLab Duo Enterprise 대응 (18 종, 모두 local)

### 1. `code_suggestions`

**용도**: 저장소 전체의 코드 개선 후보 (refactor / security finding) 를 구조화 반환.

**input schema**: (필수 항목 없음, `repo` optional)

**output (structured)**:
```json
{"suggestions": [{"file": "...", "kind": "refactor|security", "message": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:64` + `forgewise/features.py:ForgeWise.code_suggestions`

---

### 2. `duo_chat`

**용도**: 질문 토큰과 관련된 로컬 파일을 검색하여 문맥을 반환.

**input schema**:
- `question` (string, required): 질문

**output (structured)**:
```json
{"question": "...", "matches": [{"file": "...", "snippet": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:69`

---

### 3. `code_explanation` (alias)

**용도**: 파일 또는 라인 범위 설명 — 호환 alias (실제로는 `code_explanation_ide`).

**input schema**:
- `path` (string, required): 저장소 루트 기준 파일 경로
- `start` (integer, optional): 시작 라인 (1 이상)
- `end` (integer, optional): 종료 라인 (1 이상)

**output (structured)**:
```json
{"path": "...", "symbols": [...], "slice": "..."}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:77`

---

### 4. `code_explanation_ide`

**용도**: IDE 코드 설명 행에 대응 — 파일/라인 범위 + symbol 요약 + slice.

**input schema**: `code_explanation` 과 동일 (`path` required, `start` / `end` optional).

**output (structured)**: `code_explanation` 과 동일.

**Source**: `forgewise/tools.py:83`

---

### 5. `code_explanation_gitlab_ui`

**용도**: GitLab UI 문맥용 코드 설명.

**input schema**: `code_explanation` 과 동일.

**output (structured)**: `code_explanation` 과 동일.

**Source**: `forgewise/tools.py:90`

---

### 6. `refactor_code`

**용도**: 긴 함수 / 긴 줄 / broad exception 등 리팩터링 후보를 반환.

**input schema**:
- `path` (string, required): 파일 경로
- `start` / `end` (integer, optional): 라인 범위

**output (structured)**:
```json
{"path": "...", "candidates": [{"line": 42, "kind": "long_function", "message": "..."}]}
```

**Source**: `forgewise/tools.py:97`

---

### 7. `fix_code`

**용도**: 보안 finding 기반으로 자동 수정 가능한 위험 후보를 제안.

**input schema**: `refactor_code` 와 동일.

**output (structured)**:
```json
{"path": "...", "fixes": [{"line": 42, "finding": "...", "suggestion": "..."}]}
```

**Source**: `forgewise/tools.py:104`

---

### 8. `test_generation`

**용도**: Python 함수에 대한 `pytest` skeleton 생성.

**input schema**: `refactor_code` 와 동일.

**output (structured)**:
```json
{"path": "...", "skeletons": [{"function": "...", "test_source": "..."}]}
```

**Source**: `forgewise/tools.py:111`

---

### 9. `code_review`

**용도**: 저장소 전체에 대한 보안 + 유지보수성 리뷰. finding 집계.

**input schema**: (필수 항목 없음)

**output (structured)**:
```json
{"findings": [...], "severity_summary": {"high": 2, "medium": 5, "low": 10}}
```

**Source**: `forgewise/tools.py:118`

---

### 10. `root_cause_analysis`

**용도**: 스택트레이스 / 로그에서 원인 후보 파일/라인 + 마지막 에러를 추출.

**input schema**:
- `log` (string, required): 로그 경로 또는 로그 본문

**output (structured)**:
```json
{"final_error": "...", "candidates": [{"file": "...", "line": 42}]}
```

**Source**: `forgewise/tools.py:124`

---

### 11. `vulnerability_explanation`

**용도**: 취약 패턴 (`eval`, `shell=True`, hardcoded secret 등) 설명.

**input schema**: `refactor_code` 와 동일 (`path` + 선택 라인).

**output (structured)**:
```json
{"path": "...", "vulnerabilities": [{"line": 42, "pattern": "eval", "explanation": "..."}]}
```

**Source**: `forgewise/tools.py:131`

---

### 12. `vulnerability_resolution`

**용도**: 발견된 취약 패턴별 안전한 수정 방향 제시.

**input schema**: `refactor_code` 와 동일.

**output (structured)**:
```json
{"path": "...", "resolutions": [{"line": 42, "pattern": "eval", "fix": "..."}]}
```

**Source**: `forgewise/tools.py:138`

---

### 13. `merge_request_summary`

**용도**: `git diff --stat` 통계를 MR 요약으로 변환.

**input schema**:
- `base` (string, optional): 비교 기준 ref. 기본값 = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "files_changed": 5, "summary": "..."}
```

**Source**: `forgewise/tools.py:145`

---

### 14. `merge_commit_message_generation`

**용도**: `git diff` 통계를 merge commit message 초안으로 변환.

**input schema**:
- `base` (string, optional): 비교 기준 ref. 기본값 = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "message": "feat: ..."}
```

**Source**: `forgewise/tools.py:151`

---

### 15. `code_review_summary`

**용도**: 코드 리뷰 finding 수 + severity 를 요약.

**input schema**: (필수 항목 없음)

**output (structured)**:
```json
{"total_findings": 17, "severity_summary": {...}, "top_files": [...]}
```

**Source**: `forgewise/tools.py:157`

---

### 16. `issue_description_generation`

**용도**: 프롬프트를 이슈 본문 + acceptance criteria 로 변환.

**input schema**:
- `prompt` (string, required): 이슈 프롬프트

**output (structured)**:
```json
{"title": "...", "description": "...", "acceptance_criteria": [...]}
```

**Source**: `forgewise/tools.py:163`

---

### 17. `discussion_summary`

**용도**: 토론 텍스트 요약 — 줄 수, 핵심 줄, 질문 추출.

**input schema**:
- `text` (string, required): 토론 본문

**output (structured)**:
```json
{"line_count": 42, "key_lines": [...], "questions": [...]}
```

**Source**: `forgewise/tools.py:170`

---

### 18. `sdlc_trends`

**용도**: 저장소의 언어 분포 + 품질 finding 수 집계.

**input schema**: (필수 항목 없음)

**output (structured)**:
```json
{"languages": {"Python": 0.85, "Markdown": 0.10, ...}, "finding_count": 17}
```

**Source**: `forgewise/tools.py:177`

---

## Category B — GitLab MCP compatible (15 종, GitLab API proxy)

> 모든 tool 은 공통 `gitlab_base_url` / `gitlab_token` / `gitlab_timeout` property
> 를 추가로 받는다. 변경성 tool 은 `FORGEWISE_ENABLE_MUTATIONS=1` 필요 (별표 표시).

### 19. `get_mcp_server_version`

**용도**: ForgeWise MCP 서버 version / protocol / transport 반환.

**input schema**: (없음 — `accepts_repo: false`)

**output (structured)**:
```json
{"name": "forgewise", "version": "0.1.0", "protocols": ["2025-03-26", "2025-06-18"]}
```

**Source**: `forgewise/tools.py:183`

---

### 20. `create_issue` ***(변경성)***

**용도**: GitLab issue 신규 생성.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `title` (string, required): 이슈 제목
- `description` (string, optional): 이슈 설명

**output (structured)**: GitLab API `/projects/:id/issues` POST 응답.

**Source**: `forgewise/tools.py:190`

---

### 21. `get_issue`

**용도**: GitLab issue 조회.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `issue_iid` (integer, required): 이슈 IID

**output (structured)**: GitLab API `/projects/:id/issues/:iid` GET 응답.

**Source**: `forgewise/tools.py:202`

---

### 22. `create_merge_request` ***(변경성)***

**용도**: GitLab MR 신규 생성.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `title` (string, required): MR 제목
- `source_branch` (string, required): source branch
- `target_branch` (string, required): target branch
- `description` (string, optional): MR 설명

**output (structured)**: GitLab API `/projects/:id/merge_requests` POST 응답.

**Source**: `forgewise/tools.py:212`

---

### 23. `get_merge_request`

**용도**: GitLab MR 조회.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `merge_request_iid` (integer, required): MR IID

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid` GET 응답.

**Source**: `forgewise/tools.py:226`

---

### 24. `get_merge_request_commits`

**용도**: MR commit 목록 조회.

**input schema**: `get_merge_request` 와 동일.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/commits` GET 응답.

**Source**: `forgewise/tools.py:236`

---

### 25. `get_merge_request_diffs`

**용도**: MR diff 목록 조회.

**input schema**: `get_merge_request` 와 동일.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/diffs` GET 응답.

**Source**: `forgewise/tools.py:246`

---

### 26. `get_merge_request_pipelines`

**용도**: MR pipeline 목록 조회.

**input schema**: `get_merge_request` 와 동일.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/pipelines` GET 응답.

**Source**: `forgewise/tools.py:256`

---

### 27. `get_pipeline_jobs`

**용도**: Pipeline job 목록 조회.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `pipeline_id` (integer, required): Pipeline ID

**output (structured)**: GitLab API `/projects/:id/pipelines/:pid/jobs` GET 응답.

**Source**: `forgewise/tools.py:266`

---

### 28. `manage_pipeline` ***(변경성, `operation != "list"` 시)***

**용도**: Pipeline list / create / retry / cancel.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `operation` (string, required): `list` / `create` / `retry` / `cancel`
- `pipeline_id` (integer, optional): Pipeline ID (`retry`, `cancel` 시 필요)
- `ref` (string, optional): branch 또는 tag ref (`create` 시 필요)
- `variables` (object, optional): pipeline variable (key→string value)

**output (structured)**: operation 별 GitLab API 응답.

**Note**: `operation == "list"` 는 read-only — mutation gate 우회.

**Source**: `forgewise/tools.py:276`

---

### 29. `create_workitem_note` ***(변경성)***

**용도**: Work item (issue, epic, task) 에 note (comment) 신규.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `work_item_iid` (integer, required): Work item IID
- `body` (string, required): note 본문

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` POST 응답.

**Source**: `forgewise/tools.py:290`

---

### 30. `get_workitem_notes`

**용도**: Work item note 목록 조회.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `work_item_iid` (integer, required): Work item IID

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` GET 응답.

**Source**: `forgewise/tools.py:302`

---

### 31. `search`

**용도**: GitLab search API 호출.

**input schema**:
- `scope` (string, required): 검색 scope (`blobs`, `projects`, `merge_requests`, `issues`, `users` 등)
- `search` (string, required): 검색어
- `id` (string, optional): 프로젝트 ID 또는 full path (project-level search)
- `group_id` (string, optional): 그룹 ID 또는 full path (group-level search)

**output (structured)**: GitLab API search 응답.

**Source**: `forgewise/tools.py:312`

---

### 32. `search_labels`

**용도**: GitLab label 검색.

**input schema**:
- `search` (string, optional): 검색어 (생략 시 전체 label)
- `id` (string, optional): 프로젝트 ID
- `group_id` (string, optional): 그룹 ID

**output (structured)**: GitLab API label 응답.

**Source**: `forgewise/tools.py:324`

---

### 33. `semantic_code_search`

**용도**: GitLab semantic code search 호출.

**input schema**:
- `id` (string, required): 프로젝트 ID 또는 full path
- `query` (string, required): 검색 질의

**output (structured)**: GitLab API semantic search 응답.

**Source**: `forgewise/tools.py:334`

---

## 호출 예시

### stdio (직접 JSON-RPC)

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "code_review", "arguments": {"repo": "."}}}' | forgewise-mcp
```

### HTTP (curl)

```bash
curl -X POST http://127.0.0.1:8080/api/v4/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <oauth_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "code_review",
      "arguments": {"repo": "."}
    }
  }'
```

### Python client (snippet)

```python
import httpx, json

async with httpx.AsyncClient() as c:
    r = await c.post(
        "http://127.0.0.1:8080/api/v4/mcp",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "code_review", "arguments": {"repo": "."}}
        }
    )
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
```

## 다음 단계

- 설치: `docs/installation.md`
- 환경 설정: `docs/configuration.md`
- 버전 마이그레이션: `docs/upgrade.md`
- 설계 컨텍스트: `docs/design.md`
- 보안 정책: `docs/security.md` + `SECURITY.md`
