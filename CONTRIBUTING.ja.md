# 貢献ガイド (Contributing)

> [English](CONTRIBUTING.md) | [한국어](CONTRIBUTING.ko.md) | **日本語** | [中文](CONTRIBUTING.zh.md)

> このページは placeholder です。完全な日本語翻訳は別 cycle で予定 (native reviewer による品質検証含む)。
>
> See [English version](CONTRIBUTING.md) for the authoritative contribution guide.

## 概要 (Outline)

- 開発スタック: Python 3.11+ + uv + lefthook
- 環境セットアップ: `git clone` → `uv sync --extra dev` → `make setup-hooks`
- Commit: Conventional Commits + DCO `Signed-off-by:`
- ローカルゲート: `make check` (ruff + mypy + pytest)
- GitHub Actions 永久禁止 (RFC-0002)
- 詳細: [English version](CONTRIBUTING.md)
- 用語集: [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md)
