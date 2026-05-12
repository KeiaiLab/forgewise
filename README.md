# ForgeWise

ForgeWise는 GitLab Duo Enterprise류 개발 보조 기능을 오픈소스, 로컬 실행,
MCP-native 도구 표면으로 구현하는 `keiailab` 프로젝트입니다.

## 네이밍

선택 이름은 **ForgeWise**입니다.

- Forge: GitLab, GitHub, Gitea, Forgejo 같은 코드 forge 전체를 대상으로 합니다.
- Wise: 단순 챗봇이 아니라 코드 설명, 리뷰, 보안 설명, 원인 분석, 테스트 생성,
  변경 요약을 같은 정책과 감사 로그 아래에서 수행합니다.
- GitLab Duo 상표를 직접 쓰지 않고, 기능 호환 표면만 오픈소스로 제공합니다.

CLI 명령은 `forgewise`, MCP 서버 명령은 `forgewise-mcp`입니다.

## 기능 표면

현재 MVP는 외부 LLM 호출 없이 결정론적 분석으로 동작합니다. 같은 API 표면 위에
사내 LLM 또는 self-hosted 모델 라우터를 붙일 수 있게 설계했습니다.

| ForgeWise tool | 대응 기능군 |
| --- | --- |
| `code_suggestions` | 코드 제안 |
| `duo_chat` | 저장소 문맥 기반 Chat |
| `code_explanation` | 코드 설명 |
| `refactor_code` | 리팩터링 제안 |
| `fix_code` | 수정 제안 |
| `test_generation` | 테스트 생성 |
| `code_review` | 코드 리뷰 |
| `root_cause_analysis` | 장애 원인 분석 |
| `vulnerability_explanation` | 취약점 설명 |
| `vulnerability_resolution` | 취약점 해결 제안 |
| `merge_request_summary` | MR 요약 |
| `discussion_summary` | 토론 요약 |
| `sdlc_trends` | SDLC 품질 추세 |

## 설치

```bash
uv run --python 3.11 --extra dev python -m pytest
```

개발 설치:

```bash
uv sync --python 3.11 --extra dev
uv run forgewise --repo . review
```

## CLI 예시

```bash
forgewise --repo . explain forgewise/features.py
forgewise --repo . vuln-explain forgewise/security.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . check
```

`check`는 보안 또는 유지보수 finding이 있으면 exit code `1`을 반환합니다.

## MCP 서버

MCP 클라이언트에는 stdio 서버로 등록합니다.

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

각 tool 호출은 `.forgewise/audit.jsonl`에 tool 이름, 인자, 기능명을 남깁니다.
비밀값처럼 보이는 인자 키는 기록 전에 `[REDACTED]`로 마스킹합니다.

## 로컬 게이트

GitHub Actions는 사용하지 않습니다. 모든 검증은 로컬 게이트로 실행합니다.

```bash
make check
```

게이트 구성:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

자세한 설계는 [docs/design.md](docs/design.md), 근거 레퍼런스는
[docs/references.md](docs/references.md)를 봅니다.
