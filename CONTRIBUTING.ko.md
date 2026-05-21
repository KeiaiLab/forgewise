# ForgeWise 기여 가이드 (Contributing)

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> [English](CONTRIBUTING.md) | **한국어** | [日本語](CONTRIBUTING.ja.md) | [中文](CONTRIBUTING.zh.md)

**ForgeWise** — `keiailab` MCP-native 개발자 인텔리전스 도구에 기여해 주셔서
감사합니다. 본 문서는 개발 환경, commit 컨벤션, pull request flow 를 다룹니다.

> ForgeWise 는 keiailab operator family 의 유일한 Python 프로젝트입니다
> (나머지 — `valkey-operator`, `postgres-operator`, `mongodb-operator`,
> `operator-commons` — 는 Go 로 작성됩니다). Python 특이 override 는
> `AGENTS.md` 와 `docs/kb/adr/` 에 문서화되어 있습니다.

## 행동 강령

참여함으로써 본 프로젝트의 [행동 강령](CODE_OF_CONDUCT.md) 을 준수하는 데 동의합니다.
행동 강령 위반은 `conduct@keiailab.org` 로 신고해 주세요.

## 보안 이슈 신고

보안 취약점에 대해 public issue 를 **열지 마세요**. 대신 [SECURITY.md](SECURITY.md)
의 절차를 따르세요.

## 개발 환경

### 사전 조건

- **Python 3.11** 이상
- **uv** 0.4 이상 (`brew install uv` 또는
  `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **lefthook** 1.5 이상 (`brew install lefthook` 또는
  `npm install -g lefthook`)
- **git** 2.30 이상 (`git commit -s` DCO 지원 위해)

### 1회 설치

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
uv sync --extra dev      # dev dependency 설치 (ruff, mypy, pytest)
make setup-hooks         # lefthook git hook 설치
```

`make setup-hooks` 이후 다음 hook 이 활성화됩니다:

| Stage        | Hook                                                                |
| ------------ | -------------------------------------------------------------------- |
| `pre-commit` | ruff check --fix, ruff format --check, detect-secrets, markdownlint  |
| `commit-msg` | Conventional Commits regex, DCO `Signed-off-by:`                     |
| `pre-push`   | mypy --strict, pytest -q, pip-audit                                  |

`detect-secrets`, `markdownlint-cli2`, `pip-audit` 은 미설치 시 *graceful skip*
됩니다. 활성화:

```bash
uv tool install detect-secrets
uv run detect-secrets scan > .secrets.baseline    # allowlist baseline 생성
uv tool install pip-audit
npm install -g markdownlint-cli2
```

### 환경 검증

```bash
make check                       # ruff + mypy + pytest
forgewise --repo . check         # CLI smoke 실행
lefthook run pre-push --all-files
```

작업 시작 전에 셋 다 zero failure 를 보고해야 합니다.

## Commit 컨벤션

ForgeWise 는 **Conventional Commits** 와 **Developer Certificate of Origin (DCO)**
를 강제합니다. 둘 다 `lefthook` `commit-msg` 에 의해 로컬에서 검증됩니다.

### 양식

```
<type>(<scope>)?: <subject>

<body — optional, 72 컬럼에서 wrap>

Signed-off-by: Your Name <your.email@example.org>
```

| `<type>` | 사용 시점                                                      |
| -------- | ------------------------------------------------------------- |
| `feat`   | 새 사용자 가시 기능                                  |
| `fix`    | 버그 수정                                                     |
| `docs`   | 문서만                                            |
| `style`  | 포매팅만 (동작 변경 없음)                          |
| `refactor` | 동작 또는 테스트 변경 없는 코드 변경                 |
| `perf`   | 성능 개선                                       |
| `test`   | 테스트 추가 또는 수정                                       |
| `build`  | 빌드 / 패키징 / dependency 변경                         |
| `ci`     | CI / hook / 로컬 게이트 변경 (note: GitHub Actions 금지)|
| `chore`  | 일상 유지 보수 (예: 저작권 연도 업데이트)             |
| `revert` | 이전 commit 되돌리기                                  |
| `spec`   | `docs/specs/` 아래 design spec 추가 또는 수정          |

### Subject 언어

- Commit subject 와 body 는 keiailab 거버넌스 기준선 (`AGENTS.md` 가
  `~/.claude/CLAUDE.md` §2 를 참조) 에 따라 **한국어** 여야 합니다.
- 코드 식별자, 파일 이름, Conventional Commits prefix 는 영어 유지.

### Sign-off (DCO)

모든 commit 에는 `Signed-off-by:` trailer 가 포함되어야 합니다. 가장 쉬운 방법은
`git commit` 에 `-s` 를 전달하는 것:

```bash
git commit -s -m "fix(oauth): redirect URI 검증 오류 수정"
```

잊었다면 commit 을 amend:

```bash
git commit --amend -s --no-edit
```

`dco-signoff` hook 은 trailer 없는 commit 을 거부합니다. `DCO_OK=1` 로 우회
하는 것은 **강력히 권장하지 않습니다** — 우회는 사용 시 PR body 에 사유를
명시해야 합니다.

## Pull Request flow

1. **Fork 또는 branch** — 기능 작업은 `feat/<topic>-<yyyy-mm-dd>`, 버그
   수정은 `fix/<topic>-<yyyy-mm-dd>`. 날짜 suffix 는 병렬 작업 추적을 쉽게
   만듭니다.
2. **구현** — 변경은 atomic 으로; PR 당 하나의 논리적 관심사 (참조:
   `~/.claude/CLAUDE.md` §8).
3. **로컬 검증** — `make check` 와 `lefthook run pre-push --all-files`
   모두 통과해야 합니다.
4. **PR 열기** — title 은 Conventional Commits 를 따릅니다 (squash merge 가
   PR title 을 commit subject 로 사용하므로). Body 에 다음을 포함:
   - **요약 (Summary)** — what + why
   - **변경 (Changes)** — 파일 수준 표
   - **검증 증거 (Verification)** — 정확한 명령 + 요약 출력
   - **Test plan** — 테스트 항목 체크리스트
5. **리뷰** — 최소 1 명의 maintainer 리뷰. 피드백은 follow-up commit 으로
   처리 (머지 시 squash).
6. **머지** — GitHub UI 에서 squash merge, 그 후 branch 가 자동 삭제됩니다.
   PR title 이 squash commit subject 가 됩니다.

### PR 체크리스트

본 체크리스트를 PR body 에 복사하세요:

- [ ] commit message + PR body 한국어 (식별자 제외)
- [ ] 테스트 추가/수정 (regression coverage)
- [ ] `make check` 통과 (lint + typecheck + test)
- [ ] `lefthook run pre-push --all-files` 통과
- [ ] DCO `Signed-off-by:` 모든 commit 에 포함
- [ ] 변경 범위 = 의도 범위 (out-of-scope 수정 0)
- [ ] `.github/workflows/` 디렉토리 신규 0 (RFC-0002 금지)
- [ ] 외부 라이브러리 사용 시 `context7` MCP 로 최신 공식 문서 조회 증거
- [ ] 사용자 시점 시나리오 명세

## 새 MCP tool 추가

새 tool 은 **4 곳** 에 연결되어야 합니다:

1. `forgewise/tools.py` — `list_tool_definitions()` 의 `ToolDefinition`
2. `tests/test_mcp_server.py` — 등록 + 동작 assertion
3. `docs/api-reference.md` — input/output schema entry
4. `docs/design.md` — feature-group 매핑 표

이 중 어느 하나라도 빠지면 리뷰 차단입니다.

## 로컬 게이트 vs CI

ForgeWise 는 **GitHub Actions 를 사용하지 않습니다** (RFC-0002). 모든 게이트는
로컬 4 계층 enforcement 로 실행됩니다:

1. `pre-commit` hook (lefthook) — staged 파일에 대한 빠른 검사
2. `pre-push` hook (lefthook) — 게시 전 느린 검사
3. `make check` — 수동 재실행 / CI 없는 환경
4. 리뷰어 검증 — PR body 에 게이트 출력을 인용

`tests/test_governance.py` 는 `.github/workflows/` 가 추가되면 빌드를 fail
시켜 이 계약을 강제합니다.

## 버그 신고

- **보안 이슈** → [SECURITY.md](SECURITY.md) 참조.
- **기능 버그** → 재현 절차, 예상 동작, 관찰 동작, `forgewise --version` 과
  함께 GitHub issue 등록.

## 논의 채널

- 일반 질문은 GitHub Discussions
- 버그 신고 + 기능 요청은 GitHub Issues
- 파트너십 / 상업적 문의는 `support@keiailab.org` 이메일

## 향후 정책 hook

`docs/design.md` 가 참조하는 `forgewise.policy.json` 조직 정책 파일은 아직
구현되지 않았습니다. 이 파일이 도입되면, contributor 는 본 파일에 추가 정책
파일 검사를 갱신해야 합니다; 그 시점에 본 섹션이 개정될 예정입니다.
