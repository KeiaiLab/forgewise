# ブランディングガイド — `forgewise`

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> keiailab operator family の視覚的アイデンティティ、ボイス、トーン。

本文書は `forgewise` ブランディング決定の canonical な参照です。README、リリースノート、マーケティング素材、およびプロジェクトを代表するすべての第三者向けコミュニケーションに適用されます。

## 1. アイデンティティ

**組織**: [keiailab](https://keiailab.com) — Kubernetes-native データプラットフォームオペレーター (Apache-2.0, license-clean, vanilla-upstream 互換).

**プロジェクト**: `forgewise` — Apache-2.0 MCP-native 開発者インテリジェンス — オープンソース、ローカル実行、GitLab Duo Enterprise クラスのツール表面を決定論的分析で実装。

**Family**: keiailab ガバナンスベースラインを共有する 5 つの sister プロジェクトの 1 つ。`forgewise` は*唯一の Python プロジェクト* (他は Go ベースの Kubernetes オペレーター):

| プロジェクト | 言語 | ドメイン | リポジトリ |
|---|---|---|---|
| `postgres-operator` | Go | Kubernetes オペレーター (PostgreSQL 18+) | https://github.com/keiailab/postgres-operator |
| `mongodb-operator` | Go | Kubernetes オペレーター (MongoDB 7.0+) | https://github.com/keiailab/mongodb-operator |
| `valkey-operator` | Go | Kubernetes オペレーター (Valkey 8.0+) | https://github.com/keiailab/valkey-operator |
| `operator-commons` | Go | 3 オペレーター共有の Go ライブラリ | https://github.com/keiailab/operator-commons |
| **`forgewise`** | **Python 3.11+** | **MCP-native 開発者インテリジェンス** | https://github.com/keiailab/forgewise |

## 2. ロゴ + ビジュアルアセット

| アセット | URL | 用途 |
|---|---|---|
| Primary ロゴ (SVG) | `https://keiailab.com/assets/logo.svg` | README ヘッダー、スライド |
| Mono mark | `https://keiailab.com/assets/mark.svg` | Favicon、ソーシャルカード |
| Wordmark | `https://keiailab.com/assets/wordmark.svg` | Footer、dark 背景 |

**ロゴ配置**: README 上部中央、幅 120px。常に https://keiailab.com にリンク。

**Clear space**: ロゴ周辺の最小 padding = ロゴ幅の 25%。

**禁止事項**:
- ロゴの色変更
- Drop shadow / filter の追加
- コントラスト不足の背景上への配置
- keiailab ブランド承認なしに他のロゴと組み合わせ

## 3. カラーパレット

| 役割 | Hex | 用途 |
|---|---|---|
| Primary (keiailab teal) | `#0EA5A8` | ヘッダー、primary アクション、リンク |
| Secondary (deep navy) | `#0F172A` | Dark 背景、コードブロック |
| Accent (warm amber) | `#F59E0B` | ハイライト、badge アクセント |
| Neutral grey | `#64748B` | Light 背景上の本文テキスト |
| Background light | `#F8FAFC` | ドキュメントページ背景 |
| Background dark | `#020617` | コードエディタテーマ、dark mode |

GitHub README の shield.io badge は上記 hex 使用を推奨。

## 4. タイポグラフィ

- **見出し**: システムデフォルト (GitHub の default `-apple-system, BlinkMacSystemFont, Segoe UI, ...`)
- **本文**: 同上 (GitHub-native 整合)
- **コード**: `ui-monospace, SFMono-Regular, Consolas, ...` (GitHub の default monospace)

別途 webfont 使用しない (GitHub README rendering 整合)。

## 5. ボイス + トーン

**対象読者**: プラットフォームエンジニア / DevOps / SRE / 開発者体験 (DX) チーム — GitLab セルフホスト運用者または MCP-native 開発ツール評価者。

**ボイス原則**:
- **Direct** — 可能な限り段落より bullet point
- **Evidence-based** — 主張は benchmark / SLA / リンクを伴う
- **Vendor-neutral** — GitLab Duo Enterprise と機能互換だが Duo 商標または proprietary code を embed しない
- **License-aware** — Apache-2.0 + MIT/BSD/PSF 依存のみ; SaaS 表面での SSPL / コピーレフト拒否
- **Deterministic-first** — MVP は外部 LLM 呼び出し 0; 社内 LLM ルーターは opt-in attach point

**回避**:
- マーケティング最上級表現 ("blazing fast", "革新的", "最高")
- 曖昧な比較 ("X-class 品質") — *具体的なメトリクスまたはベンチマークで定量化*
- Roadmap の時間ベースの締切 (代わりに機能チェックリスト)
- GitLab 公式パートナーシップまたは Duo 商標ライセンスを示唆する主張

## 6. README ヘッダー標準

すべての README の冒頭段落は以下の形式 (Wave 3 標準 — forgewise 適応):

```markdown
<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# forgewise

> **Apache-2.0 MCP-native developer intelligence — GitLab Duo Enterprise-class tools, locally executable, deterministic**

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <!-- 既存 shield.io badges 維持 + 整合 -->
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ko.md">한국어</a> |
  <b>日本語</b> |
  <a href="README.zh.md">中文</a>
</p>
```

## 7. README Footer 標準

すべての README + root-level .md ファイルの末尾に以下の footer 添付 (Wave 3 標準 — forgewise 含む 5 repo 整合):

```markdown
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
  © 2026 keiailab · <a href="LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
```

## 8. Badge 標準順序

README の shield.io badge 順序 (左→右、forgewise 適応):

1. License (Apache-2.0)
2. Python バージョン (3.11+)
3. MCP protocol バージョン (`2025-03-26` / `2025-06-18`)
4. PyPI パッケージ (release 後)
5. Container Image (ghcr.io/keiailab/forgewise — 公開後)
6. OpenSSF Scorecard
7. GitHub Discussions

## 9. Discussions / Issues / PR テンプレート

- **Discussions**: `https://github.com/keiailab/forgewise/discussions` — 機能アイデア、Q&A
- **Issues**: バグレポート + ユースケース付き具体的機能リクエスト (セキュリティ問題は `SECURITY.md` 手順)
- **PR テンプレート**: `.github/PULL_REQUEST_TEMPLATE.md` 標準 (ユーザーシナリオ + 検証コマンド引用義務、`CONTRIBUTING.md` PR Checklist 整合)

## 10. ソーシャル + 外部

- **ウェブサイト**: https://keiailab.com
- **GitHub Org**: https://github.com/keiailab
- **PyPI** (Python パッケージ): https://pypi.org/project/forgewise/ (公開後)
- **GHCR** (コンテナ): https://github.com/keiailab/forgewise/pkgs/container/forgewise (公開後)

## 11. License + 著作権

- License: [Apache-2.0](LICENSE)
- Copyright: © 2026 keiailab contributors
- Third-party 著作権表記: see [NOTICE](NOTICE) (現在未作成 — Python deps の license 表記は `pyproject.toml` の `[project.dependencies]` と `uv.lock` で追跡)

## 12. 商標表記

- "GitLab" および "GitLab Duo" は GitLab Inc. の登録商標です。forgewise は GitLab または GitLab Inc. の公式製品 / 認定 / パートナー関係では*ありません*。
- forgewise は GitLab Duo Enterprise の*機能互換表面 (feature-compatible surface)* のみオープンソースで提供し、GitLab の proprietary code またはモデルを含みません。
- すべての GitLab API 呼び出しはユーザー自身の GitLab インスタンス + token で実行されます。

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
  © 2026 keiailab · <a href="LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
