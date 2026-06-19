# Design: Forge-neutral provider + Harbor surface + OKF knowledge layer + durable long-running operations

> Canonical: English. Translations: [한국어](2026-06-19-forge-okf-durable-design.ko.md).

| Field | Value |
|---|---|
| Date | 2026-06-19 |
| Status | Proposed |
| Author | keiailab — design cycle |
| Scope | forgewise only (valkey / postgres / mongodb / operator-commons are separate specs) |
| Follow-up | On Accepted → `docs/plans/forge-okf-durable/INDEX.md` (writing-plans output) |
| Related | `docs/design.md` (current architecture), `ROADMAP.md` (v0.2+ multi-instance / caching / SLSA L3) |
| author | keiailab <noreply@keiailab.com> |

## Change history

- **2026-06-19 v1.0**: Initial draft. Status=Proposed. Promoted to Accepted after explicit user approval.

## 1. Background

### 1.1 Where this comes from

ForgeWise today is an MCP-native re-composition of the GitLab Duo Enterprise
feature set as a local CLI plus an MCP server (`docs/design.md`). It ships a
unified catalog of **33 MCP tools** (15 GitLab REST-compatible surface + 18 Duo
compatible surface) in `forgewise/tools.py`, over two transports — stdio
(`forgewise-mcp`) and HTTP (`forgewise-http`, FastAPI, `/api/v4/mcp`) — plus the
`forgewise` CLI. Default behaviour is offline, deterministic, and makes no
external LLM call.

ForgeWise is the **5th repository of the keiailab family** — the four operators
(postgres / mongodb / valkey-operator + operator-commons, all Go) plus forgewise
(the only Python project). The MongoDB and Valkey backends referenced in this
design are the family's own operators, not third-party services.

### 1.2 The problem this design addresses

Four directions already live in `ROADMAP.md` but lack a single design of record:

1. **Forge lock-in.** GitLab-specific calls are coupled directly into the tool
   layer (`forgewise/gitlab_client.py`). The roadmap calls for "multi-instance
   (GitLab + GitHub + Bitbucket)", which needs a neutral seam first.
2. **No supply-chain surface.** Built images have no in-protocol way to report
   scan / signature status. Roadmap: "SLSA L3 (cosign keyless)".
3. **Knowledge is not portable.** Deterministic analysis results are returned
   per-call and lost; they are not expressed in any vendor-neutral, LLM-agnostic
   format.
4. **No long-running / durable execution.** A pure MCP call is synchronous and
   single-shot; a 20-minute to multi-hour job cannot be held inside one call,
   and nothing survives a crash or an LLM swap mid-task.

### 1.3 Design thesis — dual vendor neutrality

State lives in **git + OKF**, not in the LLM session.

- **MCP** defines *how an agent calls* (the interface).
- **OKF** (Open Knowledge Format) defines *how the context is expressed* (the
  knowledge). OKF is Google Cloud's vendor-neutral spec: Markdown + YAML
  frontmatter where only `type` is required.

Combining the two makes both the interface and the knowledge independent of any
single LLM. An agent becomes a **stateless worker**; the knowledge base is the
**wiki**. A run can start on Claude and resume on Grok or Codex by reading the
same bundle.

## 2. Goals + Non-Goals

### 2.1 Goals

| ID | Goal | Verification |
|---|---|---|
| G1 | Introduce a `ForgeProvider` seam; GitLab becomes the first provider, Forgejo the second — with **zero change** to the 33 public tool signatures | All 33 tools resolve through a provider; existing tests green; new `ForgeProvider` contract test passes |
| G2 | Add a **read-only Harbor surface** (image status, Trivy scan results, cosign/notation signature verification) as optional tools | Harbor tools degrade gracefully when unconfigured; read-only by default |
| G3 | Add an **OKF knowledge layer** that emits/consumes deterministic analysis as OKF bundles, git-hosted in Forgejo | A `code_review` / `vulnerability_explanation` result round-trips to a valid OKF bundle and back |
| G4 | Add **durable long-running operations** via MCP Tasks + Valkey/MongoDB so runs are resumable and cancellable | A run survives worker restart; completed steps are skipped on replay |
| G5 | Preserve every existing invariant (transports, mutation gate, audit, local gate, offline-deterministic default) | `make check` regression 0; `FORGEWISE_ENABLE_MUTATIONS` gate unchanged |

### 2.2 Non-Goals

- **Rewriting existing tools.** The 33 tool names, schemas, and behaviours are
  invariants. This design is *additive* — it inserts a seam and new optional
  surfaces beneath them.
- **Forcing external dependencies.** stdio / single-user mode must keep working
  with the standard-library core exactly as today. Valkey/MongoDB/Harbor attach
  **only** in server mode (graceful degradation).
- **Adding GitHub Actions.** RFC-0002's permanent ban stands;
  `tests/test_governance.py` continues to fail if `.github/workflows/` appears.
- **Mutating Harbor / forge state by default.** Any mutating op sits behind the
  existing `FORGEWISE_ENABLE_MUTATIONS=1` gate; the Harbor surface ships
  read-only first.
- **Implementing GitHub / Bitbucket providers now.** This spec defines the seam
  and lands GitLab + Forgejo; further providers are follow-ups.

## 3. Architecture

```
User / AI client (Claude · Grok · Codex — interchangeable)
  ├─ CLI: forgewise
  ├─ MCP stdio: forgewise-mcp
  └─ MCP HTTP: forgewise-http  /api/v4/mcp   (+ MCP Tasks handles)
          │
          ▼
ForgeWise tool layer (33 tools — names/schemas unchanged)   ← INVARIANT
          │
   ┌──────┼───────────────┬────────────────────┐
   ▼      ▼               ▼                    ▼
ForgeProvider     Harbor surface        OKF knowledge        Durable runs
(seam)            (read-only first)     (emit / consume)     (MCP Tasks)
   │                    │                    │                    │
   ├─ GitLabProvider    ├─ image status      ├─ bundle writer     ├─ task handle
   │  (gitlab_client)   ├─ Trivy scan        │  (md + YAML fm)    ├─ poll / resume / cancel
   └─ ForgejoProvider   └─ cosign verify     └─ index.md/log.md   └─ worker (journal)
          │                                        │                    │
          ▼                                        ▼                    ▼
   forge REST API                         Forgejo git (SSOT)    Valkey Streams + MongoDB
                                          + MongoDB mirror      (keiailab operators)

Default (stdio / single-user): standard-library core, offline, deterministic.   ← INVARIANT
Server mode: durable backends attach. Audit (.forgewise/audit.jsonl) always on. ← INVARIANT
```

**Additive principle.** Each new block hangs *below* the unchanged tool layer.
Remove all four and ForgeWise behaves exactly as v0.x does today.

## 4. Detailed design

### 4.1 Forge-neutral provider (`ForgeProvider`)

Today GitLab REST calls are coupled into the tool layer via
`forgewise/gitlab_client.py`. Introduce a `ForgeProvider` protocol that captures
the forge operations the 33 tools depend on (issues, merge/pull requests, MR
commits/diffs, pipelines/jobs, work-item notes, search). Tool functions call the
*active provider*, never a concrete client.

- `GitLabProvider` — wraps the existing `gitlab_client.py`; behaviour-preserving
  (the default, so current users see no change).
- `ForgejoProvider` — maps the same operations onto Forgejo's API (issues, PRs,
  Forgejo Actions, the built-in OCI/package registry).
- Selection via config/env (e.g. `FORGEWISE_FORGE=gitlab|forgejo`), one active
  provider per process.

Invariant: the 33 tool **names and JSON input schemas do not change**. The
provider is an internal seam; `tools/list` output is identical. This realizes the
roadmap's "multi-instance (GitLab + GitHub + Bitbucket)" with GitLab + Forgejo
as the first two implementations.

### 4.2 Harbor surface (read-only first)

Forgejo's built-in registry covers store/serve (OCI push/pull, Helm) but not
supply-chain security (Trivy scan, cosign/notation signing, replication,
pull-through cache). Harbor owns that surface. Add **read-only** tools that
report, not mutate:

- `harbor_image_status` — repository/tag presence, digest, push time, size.
- `harbor_scan_report` — Trivy vulnerability summary (severities, CVE list) for
  a tag.
- `harbor_signature_verify` — cosign / notation signature presence and
  verification result.

These are **optional**: when Harbor is not configured the tools degrade
gracefully (clear "not configured" result, never a hard crash), consistent with
the offline-deterministic default. Any future mutating op (e.g. tag retention)
sits behind `FORGEWISE_ENABLE_MUTATIONS=1`. This advances the roadmap's "SLSA L3
(cosign keyless)" by giving the protocol a signature-verification surface.

### 4.3 OKF knowledge layer

The deterministic analysis ForgeWise already produces (`code_review`,
`vulnerability_explanation`, `sdlc_trends`, `root_cause_analysis`, MR summaries,
…) is emitted as **OKF bundles** — Markdown + YAML frontmatter, only `type`
required — and can be consumed back as context.

Project-management knowledge is expressed as OKF concept files:

| `type` | Represents |
|---|---|
| `Project` | A repository / initiative root |
| `Milestone` | A delivery boundary |
| `Issue` | A unit of work |
| `Run` | A long-running execution (see §5) |
| `Finding` | A security / review result (from analysis tools) |
| `Runbook` | An operational procedure |

`index.md` and `log.md` interlink the concepts, so the same bundle renders as a
**board** (Projects/Issues), a **timeline** (`log.md` + Runs), and a
**knowledge graph** (cross-links). Bundles are git-hosted in Forgejo (versioned,
diffable) — the single source of truth — and mirrored to MongoDB for query.
Because the format is vendor-neutral, the knowledge is portable across Claude /
Grok / Codex with no re-encoding.

### 4.4 Durable long-running operations

A pure MCP call is synchronous; it cannot hold a multi-hour job. Two layers
solve this:

**Protocol — MCP Tasks (SEP-1391).** The Tasks extension (2026 spec RC) returns
a **durable handle** instead of blocking: the client can poll, disconnect and
reconnect to resume, and cancel. Long-running work is thus handled *within the
MCP standard*, exposed over the existing `forgewise-http` transport.

**Execution — durable worker.** Real workflows run on a durable-execution worker
(Valkey Streams + worker; Temporal / Restate / DBOS are alternatives). The
engine is **event-journal based**: after a crash, completed steps are skipped and
the run resumes. Non-deterministic LLM calls are wrapped as **activities** whose
results are journaled, so a replay reuses the recorded output rather than
re-calling the model.

Required correctness machinery (at-least-once correction):

- **Idempotency key** `(run_id + step_id)` — a replayed step is a no-op.
- **MongoDB outbox** — state change and its emitted effect commit atomically.
- **Valkey lease** — prevents two workers from running the same step.
- **Reconciliation loop** — desired ↔ actual converge after partial failure.

Backed by the keiailab `valkey-operator` (Streams/lease/cache) and
`mongodb-operator` (outbox/document store). In stdio / single-user mode these
are absent and tools run synchronously as today.

## 5. Persistence + continuity

| Concern | Mechanism | Source of truth |
|---|---|---|
| Persistence | OKF bundle in Forgejo git (version + diff + `log.md`) + MongoDB mirror | **Forgejo git** — recoverable by `git clone` if all infra dies |
| Caching / queue | Valkey (Streams, lease, cache) | Volatile — never the primary source |
| Continuity | `type: Run` + `log.md` + checkpoints | The bundle — any agent reads it and resumes |
| LLM independence | OKF (knowledge) + MCP (interface) | Neither tied to a model |

The "agent = stateless worker, knowledge = wiki" pattern means a session ending —
or swapping Claude → Grok mid-run — does not lose progress: the next agent reads
the bundle and continues from the last checkpoint.

## 6. Risks + mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Provider seam leaks GitLab-isms into tools | Forgejo provider can't satisfy contract | Define the `ForgeProvider` contract from the *tool needs*, not GitLab's API; contract test runs against both providers |
| MCP Tasks (SEP-1391) still RC | Spec may shift before GA | Keep the durable worker behind the seam; expose Tasks only on `forgewise-http`; degrade to synchronous when unsupported |
| At-least-once double effects | Duplicate side effects | Idempotency key + MongoDB outbox + Valkey lease (mandatory, not optional) |
| New optional deps (Harbor/Valkey/Mongo) creep into the core | Breaks offline-deterministic default | Hard rule: stdio/single-user imports no server deps; all server backends lazy-loaded behind config |
| OKF schema drift vs upstream | Bundles stop validating | Pin OKF v0.1; only `type` required; validate on emit |

## 7. Success criteria

```
# 1. All 33 tools resolve through ForgeProvider; names/schemas unchanged
# 2. ForgejoProvider passes the same contract test as GitLabProvider
# 3. Harbor tools return a graceful "not configured" result when Harbor absent
# 4. A code_review result round-trips to a valid OKF v0.1 bundle
# 5. A durable run survives worker restart; completed steps skipped on replay
# 6. make check regression 0; FORGEWISE_ENABLE_MUTATIONS gate unchanged
# 7. stdio/single-user mode imports no Valkey/Mongo/Harbor/FastAPI server deps
# 8. tests/test_governance.py still fails if .github/workflows/ appears
```

## 8. Out-of-scope (separate sub-projects)

- GitHub / Bitbucket providers (this spec lands the seam + GitLab + Forgejo).
- Harbor *mutating* operations (retention, GC) — read-only first.
- A specific durable engine choice (Temporal vs Valkey-native) — pluggable.
- OKF rendering UI (board/timeline/graph viewers) — the spec defines the data,
  not the viewer.

## 9. Next steps

1. Land the `ForgeProvider` seam (refactor `gitlab_client.py` behind it, no tool
   change) — smallest, highest-leverage first step.
2. Add `ForgejoProvider` + contract test.
3. Read-only Harbor surface (3 tools).
4. OKF emitter for existing analysis tools + bundle round-trip test.
5. Durable worker (Valkey Streams) + MCP Tasks handle on `forgewise-http`.
6. Wire `ROADMAP.md` / `README.md` links to this spec; add ja/zh translations.

## Appendix A. Definitions

- **OKF (Open Knowledge Format)** — Vendor-neutral knowledge format
  (Markdown + YAML frontmatter, only `type` required).
- **MCP Tasks** — MCP extension (SEP-1391) returning a durable task handle for
  long-running operations (poll / resume / cancel).
- **ForgeProvider** — Internal seam abstracting forge operations so tools are
  forge-neutral.
- **Outbox** — Pattern where a state change and its emitted effect commit
  atomically to avoid lost/duplicate effects.
- **Lease** — Short-lived exclusive claim (Valkey) preventing duplicate workers.

## Appendix B. References

- [OKF v0.1 spec — GoogleCloudPlatform/knowledge-catalog](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
- [MCP Tasks extension](https://modelcontextprotocol.io/extensions/tasks/overview)
- [SEP-1391: Long-Running Operations (MCP)](https://github.com/modelcontextprotocol/modelcontextprotocol/issues/1391)
- [Durable Execution Patterns for AI Agents (Zylos Research)](https://zylos.ai/research/2026-02-17-durable-execution-ai-agents)
- [Harbor — enterprise-grade container registry (CNCF)](https://www.cncf.io/blog/2025/12/08/harbor-enterprise-grade-container-registry-for-modern-private-cloud/)
- [Forgejo Container Registry](https://forgejo.org/docs/latest/user/packages/container/)
- Repo: `docs/design.md`, `ROADMAP.md`, `docs/configuration.md`, `docs/family.md`
