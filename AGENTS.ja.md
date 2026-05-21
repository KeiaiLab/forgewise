# AGENTS.md — ForgeWise (Tier-3 プロジェクト override) [日本語]

> [English](AGENTS.md) | [한국어](AGENTS.ko.md) | **日本語** | [中文](AGENTS.zh.md)

> このページは placeholder です。完全な日本語翻訳は別 cycle で予定 (native reviewer による品質検証含む)。
>
> See [AGENTS.md (Korean canonical)](AGENTS.md) for the authoritative Tier-3 override document.

## 概要 (Outline)

- スタック: Python 3.11+ (operator family の中で唯一の Python プロジェクト)
- パッケージマネージャ: `uv` (SSOT: `pyproject.toml`)
- Lint: `ruff check + ruff format` (line-length 100)
- Typecheck: `mypy --strict`
- テスト: `pytest -q --strict-markers`
- ローカルゲート: lefthook (pre-commit + commit-msg + pre-push)
- GitHub Actions 永久禁止 (RFC-0002)
- 詳細: [AGENTS.md (Korean canonical)](AGENTS.md)
- 用語集: [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md)
