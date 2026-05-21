# ForgeWise

> [English](README.md) | [한국어](README.ko.md) | **日本語** (placeholder) | [中文](README.zh.md) (placeholder)

ForgeWise は GitLab Duo Enterprise クラスの開発支援機能を、オープンソース、
ローカル実行、MCP-native ツール表面として実装する `keiailab` プロジェクトです。

> **状態**: `[~]` 部分実装 (placeholder) — RFC-0025 §1.2 体크박스 의미.
> native reviewer による品質検証後、`[x]` 完了状態へ昇格 candidate.

## 命名

選択名は **ForgeWise** です。

- **Forge**: GitLab、GitHub、Gitea、Forgejo といった code forge 全体を対象とします。
- **Wise**: 単なるチャットボットではなく、コード解説、レビュー、セキュリティ
  解説、原因分析、テスト生成、変更要約を同じポリシーと監査ログのもとで実行します。
- GitLab Duo 商標を直接使わず、機能互換表面のみをオープンソースで提供します。

CLI コマンドは `forgewise`、stdio MCP server コマンドは `forgewise-mcp`、HTTP
MCP server コマンドは `forgewise-http` です。

## 機能表面

詳細は [English README](README.md) の "Feature Surface" 表を参照。
本 placeholder は機能表 native 翻訳が完了次第拡張されます。

## インストール / CLI / MCP / Local Gate

詳細は [English README](README.md) を参照。Native reviewer による翻訳完了後に
本 placeholder は完全版へ拡張されます。

## 参照

- [English README](README.md) — canonical SSOT
- [한국어 README](README.ko.md) — 韓国語版
- [Glossary (日本語)](../operator-commons/docs/i18n/glossary-ja.md) — 標準用語集
  (operator-commons リポジトリ、placeholder 状態)

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
