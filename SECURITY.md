# Security Policy

## Supported Versions

The ForgeWise team provides security updates for the following versions:

| Version | Support Status |
|---------|----------------|
| 0.2.x (current) | ✅ Active security support |
| 0.1.x | ✅ Security fixes only |
| < 0.1.0 | ❌ Unsupported (pre-MVP) |

Python 3.11+ is required. Older Python versions are not security-supported.

## Reporting a Vulnerability

We take security reports seriously. If you discover a security vulnerability, please report it privately before public disclosure.

### How to Report

**Preferred Method**: GitHub private vulnerability reporting at https://github.com/keiailab/forgewise/security/advisories — click "Report a vulnerability".

**Alternative**: Email the maintainer (see `pyproject.toml` `authors` field). Use the subject prefix `[ForgeWise Security]`.

### What to Include

- Affected version(s) and component (`forgewise.mcp_server`, `forgewise.http_server`, `forgewise.llm.*`, etc.)
- Vulnerability type (auth bypass, injection, secret leak, audit log gap, etc.)
- Reproduction steps with minimal example
- Expected vs actual behavior
- Suggested mitigation (optional)
- Whether the issue affects ForgeWise core or only optional LLM provider integration

We will acknowledge receipt within 7 days and provide an initial assessment within 14 days.

## Security Boundaries

ForgeWise is designed with explicit security boundaries documented in `docs/design.md` "엔터프라이즈 경계":

### Default Boundary

- **Offline / deterministic by default**: no external LLM calls without explicit opt-in
- **Token masking**: secret values are masked in audit logs before write
- **Mutation gating**: GitLab REST API mutations require `FORGEWISE_ENABLE_MUTATIONS=1`
- **Audit log**: all tool invocations recorded to `.forgewise/audit.jsonl`

### Optional External LLM Boundary (ADR-0001)

When NVIDIA NIM provider is opted-in (`LLM_PROVIDER=nvidia` + `NVIDIA_API_KEY`):

- Only tools with `requires_llm=True` annotation may invoke external LLM
- API key is masked in audit log (fingerprint only)
- Rate-limit aware backoff + retry (429 → exponential, max 4 retry)
- Graceful degradation to deterministic mode on quota / network failure
- Audit log captures: model name, prompt SHA-256, response size, latency, masked API key fingerprint

### Known Limitations

- ForgeWise does **not** sandbox tool execution. Tool authors are responsible for validating inputs.
- The OAuth implementation (HTTP transport) follows RFC 7591 (DCR) but has not been independently audited.
- Vulnerability rules are Python-centric in the current MVP. Other languages have limited analyzer coverage.
- ForgeWise does **not** automatically apply patches. All mutation operations return suggestions for human review.

## Coordinated Disclosure

We follow a 90-day coordinated disclosure timeline for confirmed vulnerabilities. Public disclosure may be advanced if:

- A working fix is available and deployed
- The vulnerability is already publicly exploited
- The reporter requests earlier disclosure

We credit reporters in `CHANGELOG.md` "Security" section unless anonymity is requested.

## Cryptographic Components

ForgeWise relies on:

- Python `hashlib` for SHA-256 (audit log prompt fingerprinting)
- `httpx` for TLS connections to external API (NVIDIA NIM, GitLab)
- `secrets` module for OAuth nonce / state generation

No custom cryptographic primitives are implemented. All cryptographic operations use Python standard library or audited third-party packages.
