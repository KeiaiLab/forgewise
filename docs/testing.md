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
- CLI JSON 출력과 `check` 실패 exit code
- GitHub Actions 금지와 제품 문서 존재
