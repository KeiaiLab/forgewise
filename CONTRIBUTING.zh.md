# 贡献指南 (Contributing)

> [English](CONTRIBUTING.md) | [한국어](CONTRIBUTING.ko.md) | [日本語](CONTRIBUTING.ja.md) | **中文**

> 本页面是 placeholder. 完整中文翻译将在单独 cycle 中完成 (含 native reviewer 质量验证).
>
> See [English version](CONTRIBUTING.md) for the authoritative contribution guide.

## 概要 (Outline)

- 开发栈: Python 3.11+ + uv + lefthook
- 环境配置: `git clone` → `uv sync --extra dev` → `make setup-hooks`
- Commit: Conventional Commits + DCO `Signed-off-by:`
- 本地 gate: `make check` (ruff + mypy + pytest)
- GitHub Actions 永久禁用 (RFC-0002)
- 详细: [English version](CONTRIBUTING.md)
- 术语表: [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md)
