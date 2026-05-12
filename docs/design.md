# ForgeWise 설계

작성일: 2026-05-12

## 목표

ForgeWise는 GitLab Duo Enterprise 기능군을 특정 상용 forge에 묶지 않고,
로컬 CLI와 MCP 서버로 재구성합니다. 목표는 제품명을 복제하는 것이 아니라 다음
사용자 시나리오를 오픈소스 저장소 안에서 실행 가능하게 만드는 것입니다.

1. 개발자는 저장소를 외부 SaaS에 업로드하지 않고 코드 설명, 리뷰, 테스트 생성,
   취약점 설명을 실행한다.
2. AI 클라이언트는 MCP tool 목록을 통해 같은 기능을 호출한다.
3. 모든 tool 호출은 감사 로그로 남고, 비밀값은 로그에 남기지 않는다.
4. 팀은 GitHub Actions 없이 로컬 `make check`로 lint, typecheck, test를 증명한다.

## 기능 매핑

| GitLab Duo 기능군 | ForgeWise tool | MVP 동작 |
| --- | --- | --- |
| Code Suggestions | `code_suggestions` | 저장소 전체 refactor/security 후보를 구조화 반환 |
| Non-Agentic Chat | `duo_chat` | 질문 토큰과 관련 파일을 로컬 검색 |
| Code Explanation | `code_explanation` | 파일 또는 라인 범위, symbol 요약, slice 반환 |
| Refactor Code | `refactor_code` | 긴 함수, 긴 줄, broad exception 후보 반환 |
| Fix Code | `fix_code` | 보안 finding 기반 수정 방향 반환 |
| Test Generation | `test_generation` | Python 함수별 pytest skeleton 생성 |
| Code Review | `code_review` | 보안과 유지보수성 finding 집계 |
| Root Cause Analysis | `root_cause_analysis` | stack trace 파일/라인과 마지막 에러 추출 |
| Vulnerability Explanation | `vulnerability_explanation` | `eval`, `shell=True`, hardcoded secret 설명 |
| Vulnerability Resolution | `vulnerability_resolution` | finding별 안전한 수정 방향 제안 |
| Merge Request Summary | `merge_request_summary` | `git diff --stat` 기반 변경 요약 |
| Discussion Summary | `discussion_summary` | 토론 줄 수, 핵심 줄, 질문 추출 |
| SDLC Trends | `sdlc_trends` | 언어 분포와 finding 수 집계 |
| Merge Commit Message Generation | `merge_commit_message_generation` | diff 통계를 commit message 초안으로 변환 |
| Code Review Summary | `code_review_summary` | review finding 수와 severity 요약 |
| Issue Description Generation | `issue_description_generation` | 프롬프트를 이슈 본문과 acceptance criteria로 변환 |

## 아키텍처

```
사용자 / AI 클라이언트
  ├─ CLI: forgewise
  └─ MCP stdio: forgewise-mcp
          │
          ▼
ForgeWise feature layer
  ├─ repository scanner
  ├─ code explanation / retrieval
  ├─ security analyzer
  ├─ review / MR summary / root cause
  └─ audit logger
          │
          ▼
로컬 저장소 파일 + .forgewise/audit.jsonl
```

런타임 의존성은 Python 표준 라이브러리만 사용합니다. pytest, ruff, mypy는 개발
게이트 전용입니다. 이 선택은 self-hosted 환경, 폐쇄망, 사내 forge에 이식하기 쉽게
하기 위한 것입니다.

## MCP 계약

`forgewise.mcp_server`는 MCP 2025-06-18 기준의 JSON-RPC tool 표면을 제공합니다.

- `initialize`: `tools` capability와 serverInfo 반환
- `tools/list`: 16개 tool 이름, 설명, JSON inputSchema 반환
- `tools/call`: JSON text content와 `structuredContent`를 함께 반환

민감한 작업은 아직 실제 파일을 수정하지 않고 제안만 반환합니다. 자동 수정은 후속
버전에서 사용자 승인, patch preview, policy gate가 들어간 뒤 추가합니다.

## 엔터프라이즈 경계

- 기본 동작은 오프라인, 결정론적, 외부 LLM 미호출입니다.
- `.forgewise/audit.jsonl`은 tool 호출 감사를 위한 최소 로그입니다.
- 비밀값 키는 감사 로그 기록 전에 마스킹합니다.
- GitHub Actions를 만들지 않습니다. `Makefile` 기반 로컬 게이트가 source of truth입니다.
- 취약점 규칙은 지금은 Python 중심 MVP입니다. 규칙 엔진은 language별 analyzer로 확장합니다.

## 후속 확장

1. OpenAI-compatible provider router와 사내 vLLM/Ollama 연결
2. GitLab/Gitea/GitHub MR API adapter
3. tree-sitter 기반 다언어 symbol index
4. 승인 기반 patch 적용 tool
5. 조직 정책 파일 `forgewise.policy.json`
