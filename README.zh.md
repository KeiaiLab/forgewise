# ForgeWise

> [English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md) (placeholder) | **中文** (placeholder)

ForgeWise 是一个 `keiailab` 项目,以开源、本地执行、MCP-native 工具表面方式
实现 GitLab Duo Enterprise 类开发辅助功能。

> **状态**: `[~]` 部分实现 (placeholder) — RFC-0025 §1.2 复选框含义.
> native reviewer 质量验证后升级到 `[x]` 完成状态 candidate.

## 命名

选定名称为 **ForgeWise**。

- **Forge**: 面向所有 code forge — GitLab、GitHub、Gitea、Forgejo。
- **Wise**: 不是简单的聊天机器人,在相同策略和审计日志下执行代码解释、审查、
  安全解释、根因分析、测试生成、变更摘要。
- 不直接使用 GitLab Duo 商标,仅提供开源功能兼容表面。

CLI 命令为 `forgewise`,stdio MCP server 命令为 `forgewise-mcp`,HTTP MCP server
命令为 `forgewise-http`。

## 功能表面

详见 [English README](README.md) 的 "Feature Surface" 表。
本 placeholder 在功能表 native 翻译完成后扩展。

## 安装 / CLI / MCP / Local Gate

详见 [English README](README.md)。Native reviewer 翻译完成后本 placeholder
将扩展为完整版本。

## 参考

- [English README](README.md) — canonical SSOT
- [한국어 README](README.ko.md) — 韩文版
- [Glossary (中文)](../operator-commons/docs/i18n/glossary-zh.md) — 标准术语表
  (operator-commons 仓库,placeholder 状态)

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">© 2026 keiailab · Apache-2.0 · <a href="https://keiailab.com">keiailab.com</a></p>
