# Completion Audit

작성일: 2026-05-12

## Objective

GitLab Duo/MCP 엔터프라이즈 개발 보조 기능을 오픈소스로 구현한다. 네이밍부터
정하고, 다른 오픈소스 프로젝트를 참고하며, `keiailab`에 저장소를 만들고 설계,
구현, 문서, 테스트를 증거 기반으로 완료한다.

## Prompt-to-artifact checklist

| 요구사항 | 산출물 | 증거 |
| --- | --- | --- |
| 네이밍 결정 | `ForgeWise` | `README.md`의 네이밍 섹션 |
| GitLab Duo Enterprise 기능 매핑 | Duo canonical tool + 호환 alias | `docs/design.md` 기능 매핑 표, `tests/test_mcp_server.py` tool set 검증 |
| MCP 구현 | `forgewise-mcp`, `forgewise-http` | stdio/HTTP가 shared registry 사용, `/api/v4/mcp` 테스트 |
| GitLab MCP server 호환 | GitLab MCP compatible tools | issue/MR/pipeline/work item/search tools와 GitLab adapter 테스트 |
| OAuth DCR | `/oauth/register`, `/oauth/authorize`, `/oauth/token` | `tests/test_http_server.py` |
| CLI 구현 | `forgewise` | `forgewise/cli.py`, `tests/test_cli.py` |
| 오픈소스 참고 | Tabby, Continue, Aider, OpenHands | `docs/references.md` |
| keiailab 저장소 생성 | `keiailab/forgewise` | `origin=https://github.com/keiailab/forgewise.git` |
| 설계 문서 | `docs/design.md` | GitLab Duo/MCP 계약, 엔터프라이즈 경계 |
| 구현 코드 | `forgewise/*.py` | repository, analysis, security, features, MCP, HTTP, OAuth, GitLab client, CLI |
| 문서 | `README.md`, `docs/*.md` | install, CLI, MCP, testing, references |
| 테스트 | `tests/*.py` | repository/features/MCP/CLI/governance 테스트 |
| GitHub Actions 금지 | workflow 없음 | `tests/test_governance.py`, `gh api .../actions/workflows` 결과 `0` |
| 로컬 게이트 | `make check` | ruff, mypy, pytest 통합 실행 |

## Latest local verification

아래 명령을 완료 조건으로 사용한다.

```bash
make check
```

기대 출력:

```text
ruff check . -> All checks passed!
mypy forgewise tests -> Success
python -m pytest -> all tests passed
```

## Scope notes

- GitLab Duo 상표나 UI는 복제하지 않는다. 기능군을 오픈소스 CLI/MCP 계약으로 매핑한다.
- Amazon Q add-on 기능은 별도 제품 add-on이므로 ForgeWise core 완전 구현 범위에서 제외한다.
- 자동 파일 수정은 아직 제안만 반환한다. patch 적용은 사용자 승인과 policy gate가 들어간 뒤
  후속 버전에서 추가한다.
- 변경성 GitLab API tool은 `FORGEWISE_ENABLE_MUTATIONS=1`이 없으면 실패한다.
- 실제 GitLab smoke는 `FORGEWISE_LIVE_GITLAB_TOKEN`과 `FORGEWISE_LIVE_PROJECT_ID`가 있을 때만
  `make smoke-gitlab`로 실행한다.
