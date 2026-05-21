# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- ADR-0001 (Accepted) — NVIDIA NIM optional LLM provider (opt-in, audit-bound). `forgewise/docs/adr/0001-nvidia-nim-optional-provider.md`.
- Multi-language documentation (English canonical + Korean / Japanese / Chinese).
- BRANDING.md — keiailab family branding header / footer standard.
- docs/family.md — 5-repo family cross-link (postgres-operator / mongodb-operator / valkey-operator / operator-commons / forgewise).
- `forgewise/llm/` package — `LLMProvider` Protocol + `DeterministicProvider` (default) + `NVIDIANIMProvider` (opt-in, OpenAI-compatible).
- `docs/nvidia-setup.md` (+ ko/ja/zh) — NVIDIA NIM API free tier signup path. Refers to build.nvidia.com official terms (terms subject to change).

### Changed

- Tool registry — each tool now declares `requires_llm: bool` annotation (default `False`). Only `requires_llm=True` tools may invoke external LLM providers.
- `forgewise.audit` — extended to capture external LLM call metadata (model / prompt SHA / response size / latency / masked API key fingerprint).

### Security

- External LLM calls are *opt-in only*. Requires both `LLM_PROVIDER=nvidia` and `NVIDIA_API_KEY` environment variables, plus per-tool `requires_llm=True` annotation.
- Mutation tools still require `FORGEWISE_ENABLE_MUTATIONS=1`. Audit log is mandatory and call-blocking on log write failure.

## [0.1.0] — initial MVP

### Added

- MCP server (stdio + HTTP) — `forgewise-mcp`, `forgewise-http`.
- GitLab Duo Enterprise compatible tool surface (18 tools).
- GitLab MCP server compatible tool surface (12 tools).
- Audit logging — `.forgewise/audit.jsonl`.
- OAuth DCR / authorization code / token endpoint (HTTP transport).
- Default behavior: offline, deterministic, no external LLM calls (`docs/design.md` "엔터프라이즈 경계").

[Unreleased]: https://github.com/keiailab/forgewise/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/keiailab/forgewise/releases/tag/v0.1.0
