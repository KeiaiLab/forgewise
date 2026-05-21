# Plan: forgewise governance + ops alignment

| 메타 | 값 |
|---|---|
| 날짜 | 2026-05-21 |
| spec | `docs/specs/2026-05-21-forgewise-governance-and-ops-alignment-design.md` (PR #2 머지) |
| 상태 | In Progress |
| author | TaeHwan Park <eightynine01@gmail.com> |

## Phase 진행표

| Phase | 주제 | branch | PR | 상태 |
|---|---|---|---|---|
| 0 | pre-flight (spec merge + baseline) | — | #2 | done @ 056269d |
| 1 | lefthook.yml + setup-hooks | `feat/lefthook-python-4layer-2026-05-21` | #3 | done @ 02e9ad3 |
| 2 | 거버넌스 5 종 파일 | `feat/governance-5-files-2026-05-21` | TBD | done @ 59f1585 (PR 생성 대기) |
| 3 | README ja/zh 한자 + 4-lang 일관성 | `fix/readme-multilang-cleanup-2026-05-21` | TBD | pending |
| 4 | 운영 문서 4 종 | `docs/operations-4-files-2026-05-21` | TBD | pending |
| 5 | tests/test_governance.py 갱신 | `test/e2e-governance-verification-2026-05-21` | TBD | pending |
| 6 | ADR + main tag | (main 직접 또는 별 PR) | TBD | pending |
| 7 | 정리 (branch cleanup) | — | — | pending |

## Phase 2 검증 증거 (2026-05-21)

```
$ test -f SECURITY.md && test -f CONTRIBUTING.md && test -f CODE_OF_CONDUCT.md && test -f CHANGELOG.md && test -f AGENTS.md && echo "PASS"
PASS: 5 종 거버넌스 파일 모두 존재

$ make check
ruff check .  →  All checks passed!
mypy forgewise tests  →  Success: no issues found in 22 source files
pytest  →  26 passed in 0.29s
```

| 파일 | LOC | 핵심 키워드 |
|---|---|---|
| `SECURITY.md` | 84 | `security@keiailab.org`, `Security Advisory`, CVSS 3.1, 마스킹 정책 |
| `CONTRIBUTING.md` | 202 | Conventional Commits, `Signed-off-by:`, lefthook 4 계층, MCP tool 4-spot 갱신 |
| `CODE_OF_CONDUCT.md` | 18 | Contributor Covenant v2.1, `conduct@keiailab.org` |
| `CHANGELOG.md` | 79 | Keep a Changelog v1.1.0, `[Unreleased]`, `[0.1.0]` |
| `AGENTS.md` | 191 | Tier-3 Python override, RFC-0001 부트스트랩, ADR 0001 인용 |

총 574 LOC 신규.

## task 분해

- Phase 1: research/phase-1-lefthook.md
- Phase 2: research/phase-2-governance-files.md
- Phase 3: research/phase-3-readme-multilang.md
- Phase 4: research/phase-4-operations-docs.md
- Phase 5: research/phase-5-test-governance.md
- Phase 6: research/phase-6-adr.md

## atomic 정책

각 phase 1 PR = 1 squash merge. PR description 에 verification 증거 (명령 + 출력) 인용.

## verification 명령 (spec §6)

```bash
test -f SECURITY.md CONTRIBUTING.md CODE_OF_CONDUCT.md CHANGELOG.md AGENTS.md
test -f lefthook.yml && grep -q setup-hooks Makefile
test $(grep -c '體' README.ja.md) -eq 0
test -f docs/installation.md docs/configuration.md docs/api-reference.md docs/upgrade.md
uv run python -m pytest tests/test_governance.py -v
make check
grep -A1 Status docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md | grep -q Accepted
```
