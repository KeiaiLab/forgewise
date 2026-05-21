# Security Policy

ForgeWise is a `keiailab` open-source MCP-native developer intelligence tool
that may handle source code, audit logs, GitLab tokens, and OAuth credentials.
We take security seriously and appreciate responsible disclosure.

## Supported Versions

Only the latest minor release of the `0.x` series receives security patches
during the alpha phase. Once `1.0.0` ships, we will adopt a longer-term
support window (see `docs/upgrade.md`).

| Version | Supported          |
| ------- | ------------------ |
| `0.1.x` | Yes (current)      |
| `< 0.1` | No                 |

## Reporting a Vulnerability

**Please do not file public GitHub issues for security reports.**

Send the report to **security@keiailab.org** with one of the following channels:

1. **Preferred — GitHub Security Advisory**
   File a private advisory at
   <https://github.com/keiailab/forgewise/security/advisories/new>.
   This keeps the report private until a fix is published.
2. **Email** — `security@keiailab.org`. PGP key is published on the
   organization website.

Include the following:

- ForgeWise version (output of `forgewise --version`)
- Environment (OS, Python version, transport — stdio / HTTP)
- Reproduction steps or proof-of-concept
- Impact assessment (data exposure, RCE, auth bypass, etc.)

## Response SLO

| Step                                | Target                |
| ----------------------------------- | --------------------- |
| Acknowledge receipt                 | 3 business days       |
| Initial triage + severity rating    | 7 business days       |
| Patch or documented mitigation      | 30 days from triage   |
| Public advisory + CHANGELOG entry   | At patch release      |

Severity follows CVSS 3.1. Critical (CVSS >= 9.0) issues may receive an
out-of-band release.

## Known Security Boundaries

See `docs/security.md` for the full operational baseline. Highlights:

- **Mutation gate** — Tools that mutate remote state (`create_issue`,
  `create_merge_request`, `manage_pipeline`, `create_workitem_note`) are
  blocked unless `FORGEWISE_ENABLE_MUTATIONS=1`.
- **OAuth scope** — HTTP transport supports OAuth 2.0 Dynamic Client
  Registration with PKCE (`plain` / `S256`). Redirect URIs are restricted to
  `https://`, `127.0.0.1`, and `localhost`.
- **Audit log masking** — `.forgewise/audit.jsonl` redacts arguments whose
  keys match `token`, `secret`, `password`, or `key` to `[REDACTED]`.
- **Prompt-to-artifact policy** — Tool outputs are deterministic. No external
  LLM call is made by the MVP; consult `docs/security.md` if you attach an
  in-house LLM router.

## CVE Handling

- Confirmed CVEs are tracked in the project's GitHub Security tab.
- A `Security` section is added to `CHANGELOG.md` referencing the advisory
  ID and CVE identifier.
- Downstream consumers should subscribe to the GitHub Security Advisory feed
  for this repository.

## If You Suspect a Token or Secret Leak

1. Immediately revoke the affected GitLab token (or other credential) in the
   originating system.
2. Inspect `.forgewise/audit.jsonl` — the redaction layer should have masked
   the value. If a non-masked value appears, report it as a P0 vulnerability.
3. File a Security Advisory using the channels above.

---

*This policy is licensed under Apache-2.0 along with the rest of the project.*
