<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# keiailab operator family

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> 単一のガバナンスベースラインを共有する 5 つの sister プロジェクト — `operator-commons` (Go) を基盤とする Kubernetes オペレーター 3 種 + MCP-native 開発者インテリジェンスツール 1 種 (`forgewise`, Python).

本ページは **`forgewise`** リポジトリから読んでいる family canonical cross-link です。

## Family 概要

| プロジェクト | 言語 | ドメイン | 状態 | リポジトリ |
|---|---|---|---|---|
| **`postgres-operator`** | Go | Kubernetes オペレーター (PostgreSQL 18+) | active | https://github.com/keiailab/postgres-operator |
| **`mongodb-operator`** | Go | Kubernetes オペレーター (MongoDB 7.0+) | active | https://github.com/keiailab/mongodb-operator |
| **`valkey-operator`** | Go | Kubernetes オペレーター (Valkey 8.0+, Redis fork BSD-3) | active | https://github.com/keiailab/valkey-operator |
| **`operator-commons`** | Go | 3 オペレーター共有の Go ライブラリ | v0.7.0 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | Python 3.11+ | MCP-native 開発者インテリジェンス (GitLab Duo Enterprise 互換) | active (0.1.x alpha) | https://github.com/keiailab/forgewise |

## 共有ポリシー

5 プロジェクトすべてはスタックが異なっても同じガバナンスプリミティブに収束します:

- **MIT** 全体 — SSPL 不使用、SaaS 表面のコピーレフト不使用
- **ローカル 4 層ゲート** — pre-commit + pre-push + Makefile + レビュアー証拠 (`RFC-0002`, GitHub Actions 永久禁止)
- **i18n 4-lang** — README + canonical 文書 英語 / 한국어 / 日本語 / 中文 (cleanup supercycle Wave 4, 2026-05-21)
- **DCO + Conventional Commits** — すべての commit に `Signed-off-by:` + `<type>(<scope>)?: <subject>` 形式
- **韓国語の commit message + PR body** — keiailab ガバナンスベースライン (`~/.claude/CLAUDE.md` §2)
- **Plan/Spec/ADR 追跡** — プロジェクト別 `docs/plans/` + `docs/specs/` + `docs/kb/adr/`、クロスプロジェクトガバナンスは `~/.claude/rfcs/`

## `forgewise` の独自性

`forgewise` は family で唯一の非 Go プロジェクトです。スタックの違いは以下に文書化:

| 領域 | Operator family (Go) | `forgewise` (Python) |
|---|---|---|
| パッケージマネージャー | `go mod` | `uv` (SSOT: `pyproject.toml`) |
| Lint | `gofmt + go vet + golangci-lint` | `ruff check + ruff format` |
| Typecheck | `staticcheck` | `mypy --strict` |
| テストランナー | `go test -race ./...` | `pytest -q --strict-markers` |
| Audit | `govulncheck` | `pip-audit` |
| 配布 | Helm chart + OLM bundle | PyPI パッケージ + コンテナイメージ (GHCR, 予定) |
| ランタイム | Kubernetes controller-runtime | MCP サーバー (stdio + HTTP/FastAPI/OAuth 2.0 DCR) |

詳細な逸脱理由 + override matrix: `AGENTS.md` (Tier-3 override) + `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md`.

## 禁止ポリシー

- ❌ **release gate 用 GitHub Actions** — ローカル 4 層 enforcement (RFC-0002 参照、インシデント I-2026-04-28: GHA billing SPOF)
- ❌ **upstream proprietary code の embed** — `forgewise` は GitLab Duo Enterprise の*機能互換表面*のみ提供、Duo 商標 / proprietary code / モデル重みを含まない
- ❌ **MVP の外部 LLM 呼び出し** — `forgewise` MVP は決定論的 (LLM 呼び出し 0)、社内 LLM ルーターは opt-in attach point のみ
- ❌ **Roadmap の時間ベースの締切** — 代わりに機能チェックリスト + 完成度 %

## 開始点 (`forgewise` 特有)

| タスク | Entry point |
|---|---|
| インストール + 環境検証 | [docs/installation.md](installation.md) |
| MCP client 設定 + OAuth | [docs/configuration.md](configuration.md) |
| 33 種 MCP tool カタログ | [docs/api-reference.md](api-reference.md) |
| アップグレード / マイグレーションポリシー | [docs/upgrade.md](upgrade.md) |
| 設計コンテキスト | [docs/design.md](design.md) |
| セキュリティベースライン | [docs/security.md](security.md) + [SECURITY.md](../SECURITY.md) |
| Issue / 機能リクエスト | https://github.com/keiailab/forgewise/issues |
| 設計 / ロードマップ議論 | https://github.com/keiailab/forgewise/discussions |
| コード貢献 | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| セキュリティ問題報告 | [SECURITY.md](../SECURITY.md) |
| ブランド / ボイス | [BRANDING.md](../BRANDING.md) |
| リリース履歴 | [CHANGELOG.md](../CHANGELOG.md) |
| プロジェクト特有 AI override | [AGENTS.md](../AGENTS.md) (Tier-3) |

## Cross-family 互換性

3 つのデータベースオペレーターは `github.com/keiailab/operator-commons` を同じバージョンで import (現在 `v0.7.0+`)。`forgewise` は operator-commons を import *しない* (Go ↔ Python 境界) が、以下を共有:

- ガバナンスベースライン (`~/.claude/CLAUDE.md` Tier-1)
- ADR / RFC / commit コンベンション
- i18n ポリシー (`operator-commons/docs/i18n/README.md` SSOT)
- 用語集 (`operator-commons/docs/i18n/glossary-{ko,ja,zh}.md`)
- pre-commit hook パターン (lefthook)

`operator-commons` の breaking change は 3 つの Go オペレーターの同期 bump が必要 — `forgewise` は API 境界では影響を受けないが、`scripts/sync-from-commons.sh` で共有 lefthook / i18n / ガバナンス更新を取得可能。

## i18n

本ページ (および全 `forgewise` canonical 文書) は 4 言語で提供:

- [English](family.md) (canonical)
- [한국어](family.ko.md)
- **日本語** (本ファイル)
- [中文](family.zh.md)

紛争時は英語版が技術内容について権威 (authoritative) を持ちます; ローカライズ版は同じ決定を母語で自然に反映します。

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">
  © 2026 keiailab · <a href="../LICENSE">MIT</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
