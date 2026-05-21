# NVIDIA NIM Setup — `nim_code_review` Tool

> ForgeWise integrates NVIDIA NIM hosted endpoints (OpenAI-compatible) for advisory code review. This guide covers free-tier signup, API key provisioning, and the `nim_code_review` tool surface.

## 1. Free-tier signup

1. Visit https://build.nvidia.com/
2. Sign in with a NVIDIA Developer Program account (free, email-only).
3. Pick any model (e.g. `meta/llama-3.3-70b-instruct`) and click **Get API Key**.
4. Copy the generated `nvapi-...` token.

**Quota**: 1000 credits/month default, up to 5000 on request, 40 req/min rate limit.

## 2. Provision the API key

ForgeWise resolves the API key in this priority order:

1. Explicit `api_key=` argument to `NimClient(...)`
2. `NVIDIA_API_KEY` environment variable
3. File at `~/.secrets/nvidia/nim-api-key.txt` (mode `0600`)

The file path is the recommended SSOT for local development (no env leakage):

```bash
mkdir -p ~/.secrets/nvidia
echo "nvapi-XXXXXXXXXXXXXXXXXXXXX" > ~/.secrets/nvidia/nim-api-key.txt
chmod 600 ~/.secrets/nvidia/nim-api-key.txt
```

## 3. Use the `nim_code_review` MCP tool

Once the key is provisioned, the tool is available via the MCP surface:

```json
{
  "name": "nim_code_review",
  "arguments": {
    "code": "def divide(a, b):\n    return a / b",
    "focus": "security",
    "model": "meta/llama-3.3-70b-instruct"
  }
}
```

### Arguments

| Field   | Required | Description                                                            |
|---------|----------|------------------------------------------------------------------------|
| `code`  | yes      | The code snippet to review (UTF-8 text).                               |
| `focus` | no       | Review focus (`security`, `performance`, `readability`, `general`).    |
| `model` | no       | NIM model ID. Defaults to `meta/llama-3.3-70b-instruct`.               |

### Response shape

```json
{
  "advisory_review": "[critical] divide-by-zero risk...",
  "model": "meta/llama-3.3-70b-instruct",
  "credits_remaining": 998,
  "finish_reason": "stop",
  "trust_boundary": "advisory — caller must treat output as a hint, not authoritative."
}
```

### Error handling

The tool raises `McpToolError` with structured codes on failure:

| Error code | Symbol                  | Caller action                         |
|-----------:|-------------------------|---------------------------------------|
| -32001     | `nim_auth_failure`      | Re-provision key, verify scope        |
| -32002     | `nim_quota_exhausted`   | Wait for rate-limit reset (40/min)    |
| -32003     | `nim_upstream_error`    | Retry with backoff, check NIM status  |

There is no silent fallback: every failure surfaces explicitly to the caller.

## 4. Trust boundary

`nim_code_review` is **advisory only**. The LLM response is a hint to inform human or higher-level agent decisions. Do not treat the output as authoritative for:

- Production code changes without human review
- Security-critical merges
- Compliance audits

## 5. Model choices

NVIDIA NIM hosts 80+ models. Verified-working candidates for code review:

- `meta/llama-3.3-70b-instruct` (default — balanced quality/cost)
- `nvidia/llama-3.3-nemotron-super-49b-v1` (NVIDIA tuned)
- `mistralai/codestral-22b-v0.1` (code-specialized)

See https://build.nvidia.com/models for the full catalog.

## 6. Endpoint

`https://integrate.api.nvidia.com/v1/chat/completions` — OpenAI-compatible REST. The base URL is the only adapter ForgeWise needs; standard OpenAI tooling works as-is.

## 7. Refs

- `forgewise/nim_client.py` — HTTP client with quota/auth/upstream error class hierarchy
- `forgewise/tools.py` — `nim_code_review` tool definition + handler
- `tests/test_nim.py` — mocked endpoint test coverage (10 tests)
- Spec: https://docs.nvidia.com/nim/large-language-models/latest/
