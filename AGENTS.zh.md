# AGENTS.md — ForgeWise (Tier-3 项目 override) [中文]

> [English](AGENTS.md) | [한국어](AGENTS.ko.md) | [日本語](AGENTS.ja.md) | **中文**

> 本页面是 placeholder. 完整中文翻译将在单独 cycle 中完成 (含 native reviewer 质量验证).
>
> See [AGENTS.md (Korean canonical)](AGENTS.md) for the authoritative Tier-3 override document.

## 概要 (Outline)

- 技术栈: Python 3.11+ (operator family 中唯一的 Python 项目)
- 包管理器: `uv` (SSOT: `pyproject.toml`)
- Lint: `ruff check + ruff format` (line-length 100)
- 类型检查: `mypy --strict`
- 测试: `pytest -q --strict-markers`
- 本地 gate: lefthook (pre-commit + commit-msg + pre-push)
- GitHub Actions 永久禁用 (RFC-0002)
- 详细: [AGENTS.md (Korean canonical)](AGENTS.md)
- 术语表: [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md)
