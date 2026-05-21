# Contributing to ForgeWise

> **English** | [한국어](CONTRIBUTING.ko.md) | [日本語](CONTRIBUTING.ja.md) | [中文](CONTRIBUTING.zh.md)

Thank you for your interest in contributing to **ForgeWise** — the
`keiailab` MCP-native developer intelligence tool. This document covers
the development environment, commit conventions, and pull request flow.

> ForgeWise is the only Python project in the keiailab operator family
> (the others — `valkey-operator`, `postgres-operator`, `mongodb-operator`,
> `operator-commons` — are written in Go). Python-specific overrides are
> documented in `AGENTS.md` and `docs/kb/adr/`.

## Code of Conduct

By participating you agree to abide by our
[Code of Conduct](CODE_OF_CONDUCT.md). Conduct violations should be reported
to `conduct@keiailab.org`.

## Reporting Security Issues

Please do **not** open public issues for security vulnerabilities. Follow the
process in [SECURITY.md](SECURITY.md) instead.

## Development Setup

### Prerequisites

- **Python 3.11** or newer
- **uv** 0.4 or newer (`brew install uv` or
  `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **lefthook** 1.5 or newer (`brew install lefthook` or
  `npm install -g lefthook`)
- **git** 2.30 or newer (for `git commit -s` DCO support)

### One-time setup

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
uv sync --extra dev      # install dev dependencies (ruff, mypy, pytest)
make setup-hooks         # install lefthook git hooks
```

After `make setup-hooks` the following hooks become active:

| Stage        | Hooks                                                                |
| ------------ | -------------------------------------------------------------------- |
| `pre-commit` | ruff check --fix, ruff format --check, detect-secrets, markdownlint  |
| `commit-msg` | Conventional Commits regex, DCO `Signed-off-by:`                     |
| `pre-push`   | mypy --strict, pytest -q, pip-audit                                  |

`detect-secrets`, `markdownlint-cli2`, and `pip-audit` are *graceful skips*
when not installed. To enable them:

```bash
uv tool install detect-secrets
uv run detect-secrets scan > .secrets.baseline    # generate allowlist baseline
uv tool install pip-audit
npm install -g markdownlint-cli2
```

### Verifying the environment

```bash
make check                       # ruff + mypy + pytest
forgewise --repo . check         # smoke run of the CLI
lefthook run pre-push --all-files
```

All three should report zero failures before you start work.

## Commit Conventions

ForgeWise enforces **Conventional Commits** and the **Developer Certificate
of Origin (DCO)**. Both are checked locally by `lefthook` `commit-msg`.

### Format

```
<type>(<scope>)?: <subject>

<body — optional, wrap at 72 columns>

Signed-off-by: Your Name <your.email@example.org>
```

| `<type>` | Use when                                                      |
| -------- | ------------------------------------------------------------- |
| `feat`   | A new user-facing capability                                  |
| `fix`    | A bug fix                                                     |
| `docs`   | Documentation only                                            |
| `style`  | Formatting only (no behavior change)                          |
| `refactor` | Code change with no behavior or test change                 |
| `perf`   | Performance improvement                                       |
| `test`   | Test additions or fixes                                       |
| `build`  | Build / packaging / dependency change                         |
| `ci`     | CI / hook / local-gate change (note: GitHub Actions is banned)|
| `chore`  | Routine maintenance (e.g. bumping copyright year)             |
| `revert` | Reverting a prior commit                                      |
| `spec`   | Adding or amending a design spec under `docs/specs/`          |

### Subject language

- Commit subject and body **must be in Korean** per the keiailab governance
  baseline (`AGENTS.md` references `~/.claude/CLAUDE.md` §2).
- Code identifiers, file names, and Conventional Commits prefixes remain in
  English.

### Sign-off (DCO)

Every commit must include a `Signed-off-by:` trailer. The easiest way is to
pass `-s` to `git commit`:

```bash
git commit -s -m "fix(oauth): redirect URI 검증 오류 수정"
```

If you forgot, amend the commit:

```bash
git commit --amend -s --no-edit
```

The `dco-signoff` hook will reject commits without the trailer. Bypassing
with `DCO_OK=1` is **strongly discouraged** — the bypass must be justified
in the PR body if used.

## Pull Request Flow

1. **Fork or branch** — feature work on `feat/<topic>-<yyyy-mm-dd>`, bug
   fixes on `fix/<topic>-<yyyy-mm-dd>`. The date suffix makes parallel work
   easier to track.
2. **Implement** — keep changes atomic; one logical concern per PR (see
   `~/.claude/CLAUDE.md` §8).
3. **Local verification** — `make check` and `lefthook run pre-push
   --all-files` must both pass.
4. **Open the PR** — title follows Conventional Commits (since the squash
   merge will use the PR title as the commit subject). Body must include:
   - **요약 (Summary)** — what and why
   - **변경 (Changes)** — file-level table
   - **검증 증거 (Verification)** — exact command + abbreviated output
   - **Test plan** — checklist of what was tested
5. **Review** — at least one maintainer review. Address feedback in
   follow-up commits (squashed on merge).
6. **Merge** — squash merge from the GitHub UI, then the branch is
   automatically deleted. The PR title becomes the squash commit subject.

### PR Checklist

Copy this checklist into the PR body:

- [ ] commit message + PR body 한국어 (식별자 제외)
- [ ] 테스트 추가/수정 (regression coverage)
- [ ] `make check` 통과 (lint + typecheck + test)
- [ ] `lefthook run pre-push --all-files` 통과
- [ ] DCO `Signed-off-by:` 모든 commit 에 포함
- [ ] 변경 범위 = 의도 범위 (out-of-scope 수정 0)
- [ ] `.github/workflows/` 디렉토리 신규 0 (RFC-0002 금지)
- [ ] 외부 라이브러리 사용 시 `context7` MCP 로 최신 공식 문서 조회 증거
- [ ] 사용자 시점 시나리오 명세

## Adding a New MCP Tool

A new tool must be wired in **four** places:

1. `forgewise/tools.py` — `ToolDefinition` in `list_tool_definitions()`
2. `tests/test_mcp_server.py` — registration + behavior assertions
3. `docs/api-reference.md` — input/output schema entry
4. `docs/design.md` — feature-group mapping table

Missing any of the four is a review blocker.

## Local Gates vs. CI

ForgeWise **does not use GitHub Actions** (RFC-0002). Every gate runs
locally in a 4-layer enforcement:

1. `pre-commit` hook (lefthook) — fast checks on staged files
2. `pre-push` hook (lefthook) — slow checks before publishing
3. `make check` — manual rerun / CI-less environments
4. Reviewer verification — PR body must cite gate output

`tests/test_governance.py` enforces this contract by failing the build if
`.github/workflows/` ever appears.

## Reporting Bugs

- **Security issues** → see [SECURITY.md](SECURITY.md).
- **Functional bugs** → open a GitHub issue with reproduction steps,
  expected behavior, observed behavior, and `forgewise --version`.

## Where to Discuss

- GitHub Discussions for general questions
- GitHub Issues for bug reports and feature requests
- Email `support@keiailab.org` for partnership / commercial queries

## Future Policy Hooks

The `forgewise.policy.json` organization-policy file referenced in
`docs/design.md` is not yet implemented. When it lands, contributors will
need to update this file with the additional policy-file checks; this
section will be revised at that point.
