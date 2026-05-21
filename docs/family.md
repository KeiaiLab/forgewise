<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# keiailab open-source family

> Five sister projects: 3 Kubernetes operators + 1 shared Go library + 1 MCP-native developer intelligence tool — all Apache-2.0, all license-clean.

You are reading this from the **`forgewise`** repository. This page is the canonical cross-link for the entire family.

## Family overview

| Project | Tier | Stack | Database / Surface | Repository |
|---|---|---|---|---|
| **`operator-commons`** | Library | Go | Shared library — finalizer / labels / status / version | https://github.com/keiailab/operator-commons |
| **`postgres-operator`** | Operator | Go (controller-runtime) | PostgreSQL 18+ | https://github.com/keiailab/postgres-operator |
| **`mongodb-operator`** | Operator | Go (controller-runtime) | MongoDB 7.0+ | https://github.com/keiailab/mongodb-operator |
| **`valkey-operator`** | Operator | Go (controller-runtime) | Valkey 8.0+ (Redis fork, BSD-3) | https://github.com/keiailab/valkey-operator |
| **`forgewise`** (you are here) | MCP server | Python 3.11+ (FastAPI / httpx) | GitLab / GitHub / Gitea / Forgejo developer assistant | https://github.com/keiailab/forgewise |

## Technology stack matrix

| Aspect | 4 operator projects (commons + 3 DB) | `forgewise` |
|---|---|---|
| Language | Go 1.25+ | Python 3.11+ |
| Runtime target | Kubernetes cluster (controller-runtime + CRDs) | Local CLI + MCP stdio/HTTP server |
| Deployment | Helm chart + OLM bundle | `uvx forgewise-mcp` / `pip install forgewise` |
| Surface area | Custom resource reconciliation | MCP tool surface for code forge API |
| License | Apache-2.0 | Apache-2.0 |
| Test framework | Go `testing` + envtest + Kuttl | pytest |

## What we share

All five projects converge on shared operational primitives:

- **Apache-2.0** end-to-end — no SSPL, no AGPL, no BUSL, no copyleft on SaaS surface
- **No GitHub Actions for release gates** — local 4-layer (lefthook pre-commit / pre-push / Makefile / PR review) + GitLab CI L5 (see RFC-0002, RFC-0043)
- **i18n** — README + canonical docs in English / 한국어 / 日本語 / 中文
- **Time-based roadmap deadlines avoided** — feature checklists + 3-state markers (see `standards/roadmap.md §1.1`)
- **No GitLab Duo trademark in product positioning** — `forgewise` provides capability surface only (see [BRANDING.md §6](../BRANDING.md))

## `forgewise` role in the family

This repository is the **MCP-native developer intelligence tool** — *not* a Kubernetes controller. It provides:

| Feature group | MCP tool surface | Tier |
|---|---|---|
| Code explanation | `explain_code`, `explain_diff` | MVP |
| Code review | `review_merge_request`, `review_commit` | MVP |
| Security explanation | `explain_security_finding`, `triage_vulnerability` | MVP |
| Root cause analysis | `rca_pipeline_failure`, `rca_test_failure` | MVP |
| Test generation | `generate_tests_for_diff` | MVP |
| Change summarization | `summarize_merge_request`, `summarize_commit_range` | MVP |

Design invariant: **deterministic-first**. The current MVP performs static analysis without external LLM calls; the same API surface allows attaching an in-house LLM or self-hosted model router later.

See [README.md](../README.md) for MCP client setup and [docs/design.md](design.md) for the detailed feature surface.

## What we do NOT do

- ❌ **Embed proprietary LLM dependencies** — bring your own model (in-house or self-hosted router) for AI-augmented modes
- ❌ **GitHub Actions for release gates** — local 4-layer + GitLab CI L5 (see RFC-0002, RFC-0043)
- ❌ **Time-based roadmap deadlines** — feature checklist + completion percentages (see `standards/roadmap.md §1.1`)
- ❌ **Direct GitLab Duo brand substitution** — `forgewise` is an *open-source feature-compatible surface*, not a trademark replacement (see [BRANDING.md §6](../BRANDING.md))
- ❌ **Single-forge lock-in** — every tool surface is forge-neutral (GitLab / GitHub / Gitea / Forgejo)

## Where to start

| Task | Entry point |
|---|---|
| Install + run `forgewise` locally | [README.md](../README.md) Quickstart section |
| Read the architecture / design | [docs/design.md](design.md) |
| Read the reference grounding | [docs/references.md](references.md) |
| File an issue or feature request | https://github.com/keiailab/forgewise/issues |
| Discuss design or roadmap | https://github.com/keiailab/forgewise/discussions |
| Report a security issue | [SECURITY.md](../SECURITY.md) |
| Learn the brand / voice | [BRANDING.md](../BRANDING.md) |
| Review release history | [CHANGELOG.md](../CHANGELOG.md) |
| Read security operating standards | [docs/security.md](security.md) |
| Test plan + framework | [docs/testing.md](testing.md) |

## Cross-family compatibility

`forgewise` does not depend on the Go operator family at runtime. It can, however, consume the same MCP servers (GitLab MCP, GitHub MCP, etc.) used by the operator family for governance and audit. Cross-family integration boundaries:

| Boundary | Owner | Direction |
|---|---|---|
| Code forge API (GitLab / GitHub / Gitea / Forgejo) | `forgewise` | Read + Write |
| GitLab MCP server (keiailab-gitlab-mcp) | external | `forgewise` may consume |
| Kubernetes cluster control plane | 3 operator family | `forgewise` does NOT touch |
| `operator-commons` Go library | 3 operator family | not consumed by `forgewise` (Python) |

## i18n

This page (and all canonical project docs) is being localized to four languages over time:

- **English** (canonical, this file)
- 한국어 (planned)
- 日本語 (planned)
- 中文 (planned)

The current `forgewise` i18n cycle covers `README.md` + `README.ko.md` (active) and `README.ja.md` / `README.zh.md` (placeholder). When in doubt, the English version is authoritative for technical content; localized versions reflect the same decisions in native phrasing.

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">© 2026 keiailab · <a href="../LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a></p>
