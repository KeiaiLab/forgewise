<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# keiailab operator family

> Five sister projects sharing a single governance baseline — 3 Kubernetes operators built on `operator-commons` (Go) + 1 MCP-native developer intelligence tool (`forgewise`, Python).

You are reading this from the **`forgewise`** repository. This page is the canonical cross-link for the entire family.

## Family overview

| Project | Language | Domain | Status | Repository |
|---|---|---|---|---|
| **`postgres-operator`** | Go | Kubernetes operator (PostgreSQL 18+) | active | https://github.com/keiailab/postgres-operator |
| **`mongodb-operator`** | Go | Kubernetes operator (MongoDB 7.0+) | active | https://github.com/keiailab/mongodb-operator |
| **`valkey-operator`** | Go | Kubernetes operator (Valkey 8.0+, Redis fork BSD-3) | active | https://github.com/keiailab/valkey-operator |
| **`operator-commons`** | Go | Shared Go library for the 3 operators | v0.7.0 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | Python 3.11+ | MCP-native developer intelligence (GitLab Duo Enterprise-compat) | active (0.1.x alpha) | https://github.com/keiailab/forgewise |

## What we share

All five projects converge on the same governance primitives, even when their stacks differ:

- **Apache-2.0** end-to-end — no SSPL, no copyleft on SaaS surface
- **Local 4-layer gates** — pre-commit + pre-push + Makefile + reviewer evidence (`RFC-0002`, GitHub Actions banned)
- **i18n 4-lang** — README + canonical docs in English / 한국어 / 日本語 / 中文 (Wave 4 of cleanup supercycle 2026-05-21)
- **DCO + Conventional Commits** — every commit `Signed-off-by:` + `<type>(<scope>)?: <subject>` form
- **Korean-language commit messages + PR bodies** — keiailab governance baseline (`~/.claude/CLAUDE.md` §2)
- **Plan/Spec/ADR tracking** — `docs/plans/` + `docs/specs/` + `docs/kb/adr/` per project, with `~/.claude/rfcs/` for cross-project governance

## What is unique about `forgewise`

`forgewise` is the only non-Go project in the family. The stack difference is documented in:

| Area | Operator family (Go) | `forgewise` (Python) |
|---|---|---|
| Package manager | `go mod` | `uv` (SSOT: `pyproject.toml`) |
| Lint | `gofmt + go vet + golangci-lint` | `ruff check + ruff format` |
| Typecheck | `staticcheck` | `mypy --strict` |
| Test runner | `go test -race ./...` | `pytest -q --strict-markers` |
| Audit | `govulncheck` | `pip-audit` |
| Distribution | Helm chart + OLM bundle | PyPI package + container image (GHCR, planned) |
| Runtime | Kubernetes controller-runtime | MCP server (stdio + HTTP/FastAPI/OAuth 2.0 DCR) |

Full divergence rationale + override matrix: `AGENTS.md` (Tier-3 override) + `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md`.

## What we do NOT do

- ❌ **GitHub Actions for any release gate** — local 4-layer enforcement (see RFC-0002, incident I-2026-04-28: GHA billing SPOF)
- ❌ **Embed proprietary upstream code** — `forgewise` provides a *feature-compatible surface* to GitLab Duo Enterprise but never embeds Duo trademark, proprietary code, or model weights
- ❌ **External LLM calls in MVP** — `forgewise` MVP is deterministic (zero LLM call); in-house LLM router is an opt-in attach point only
- ❌ **Time-based roadmap deadlines** — feature checklist + completion percentages instead

## Where to start (`forgewise`-specific)

| Task | Entry point |
|---|---|
| Install + verify environment | [docs/installation.md](installation.md) |
| Configure MCP client + OAuth | [docs/configuration.md](configuration.md) |
| Browse 33 MCP tools | [docs/api-reference.md](api-reference.md) |
| Upgrade / migration policy | [docs/upgrade.md](upgrade.md) |
| Read the design context | [docs/design.md](design.md) |
| Read the security baseline | [docs/security.md](security.md) + [SECURITY.md](../SECURITY.md) |
| File an issue or feature request | https://github.com/keiailab/forgewise/issues |
| Discuss design or roadmap | https://github.com/keiailab/forgewise/discussions |
| Contribute code | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Report a security issue | [SECURITY.md](../SECURITY.md) |
| Learn the brand / voice | [BRANDING.md](../BRANDING.md) |
| Track release history | [CHANGELOG.md](../CHANGELOG.md) |
| Project-specific AI override | [AGENTS.md](../AGENTS.md) (Tier-3) |

## Cross-family compatibility

The three database operators import `github.com/keiailab/operator-commons` at the matching version (currently `v0.7.0+`). `forgewise` does *not* import operator-commons (Go ↔ Python boundary) but shares:

- governance baseline (`~/.claude/CLAUDE.md` Tier-1)
- ADR / RFC / commit conventions
- i18n policy (`operator-commons/docs/i18n/README.md` SSOT)
- glossary terminology (`operator-commons/docs/i18n/glossary-{ko,ja,zh}.md`)
- pre-commit hook patterns (lefthook)

A breaking change in `operator-commons` requires synchronized bumps across the three Go operators — `forgewise` is unaffected at the API boundary but may pick up shared lefthook / i18n / governance updates via `scripts/sync-from-commons.sh`.

## i18n

This page (and all canonical `forgewise` docs) is available in four languages:

- **English** (canonical, this file)
- [한국어](family.ko.md)
- [日本語](family.ja.md)
- [中文](family.zh.md)

When in doubt, the English version is authoritative for technical content; localized versions reflect the same decisions in native phrasing.

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">
  © 2026 keiailab · <a href="../LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
