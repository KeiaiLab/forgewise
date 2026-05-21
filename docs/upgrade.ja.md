# アップグレードガイド (Upgrade Guide)

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> [English](upgrade.md) | [한국어](upgrade.ko.md) | **日本語** | [中文](upgrade.zh.md)

ForgeWise のバージョンマイグレーションガイド。SemVer ポリシー + 将来のバージョン互換性。

## SemVer ポリシー

ForgeWise は [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) に
従います。

| 段階 | ポリシー |
|---|---|
| `0.x.y` (alpha — 現在) | minor (`y` → `y+1`) でも breaking change 可能。すべての breaking change は `CHANGELOG.md` の `### Changed` または `### Removed` セクション + 本文書のマイグレーションガイドに追加。 |
| `1.0.0` 以降 | 厳格 SemVer。MAJOR = breaking, MINOR = additive, PATCH = bug fix。 |

## 現在のバージョン

| Stream | バージョン | 状態 |
|---|---|---|
| `main` | `0.1.0` + Unreleased | アクティブ |

`CHANGELOG.md` の `[Unreleased]` セクションが次のリリース候補変更の SSOT。

## マイグレーションガイド

### vN/A → v0.1.0 (initial release)

**現在 initial release 準備中**。別途マイグレーション手順なし。

インストールは `docs/installation.md` 参照。

### v0.1.0 → v0.2.0 (placeholder)

(将来 v0.2.0 release 時点で作成。形式例:)

#### Breaking changes

(例)
- `forgewise.policy.json` 組織ポリシーファイル導入 — 不在時はデフォルトポリシー適用
- 環境変数 `FORGEWISE_OAUTH_CLIENT_ID` 新規必須 (HTTP transport + OAuth)
- MCP tool `<tool_name>` の input schema に `<param>` 追加 (required)

#### マイグレーション手順

(例)
1. `forgewise.policy.json` 作成 (template: `docs/policy-template.json`)
2. `.env` に `FORGEWISE_OAUTH_CLIENT_ID` 追加
3. MCP client の `<tool_name>` 呼び出し site に `<param>` 追加
4. `make check` + `forgewise --repo . check` 回帰検証

#### 環境変数マッピング

| v0.1.0 | v0.2.0 | 備考 |
|---|---|---|
| `<old_var>` | `<new_var>` | (例) rename — 既存変数は 1 release 期間 deprecated alias 維持 |

#### MCP tool 名マッピング

| v0.1.0 | v0.2.0 | 備考 |
|---|---|---|
| `<old_tool>` | `<new_tool>` | (例) rename — alias を 1 release 維持 |

### vN → vN+1 (general template)

新 minor / major release ごとに本セクション追加:

```markdown
### v<old> → v<new> (<release date>)

#### Breaking changes
- ...

#### マイグレーション手順
1. ...

#### 環境変数マッピング
| <old> | <new> | 備考 |

#### MCP tool 名マッピング
| <old> | <new> | 備考 |

#### データ互換性
- `.forgewise/audit.jsonl` 形式変更時、自動マイグレーションスクリプト仕様
- その他永続データ (DB, cache) マイグレーション
```

## 依存関係更新

`uv.lock` は SSOT。依存関係更新:

```bash
# すべての依存関係を latest compatible に更新
uv sync --upgrade

# 回帰検証
make check

# 差分確認
git diff uv.lock pyproject.toml

# 変更なしなら commit、回帰ありなら lockfile のみ restore:
# git checkout uv.lock pyproject.toml
```

major version bump が発生した dependency は PR body に `<dep>: vN → vN+1` 明記。
breaking change が疑わしい dep (uvicorn / fastapi / authlib / httpx) は別 PR で
分離し回帰リスクを隔離。

## MCP protocol 更新

ForgeWise は以下の MCP protocol version をネゴシエート (`forgewise/mcp_server.py` の
`initialize` 応答):

- `2025-03-26` (legacy)
- `2025-06-18` (current)

新 protocol spec 導入時:

1. `forgewise/mcp_server.py` の `_NEGOTIATED_PROTOCOL_VERSIONS` 更新
2. 新 spec の capability 差分を本文書にマイグレーションガイド追加
3. legacy protocol サポート deprecate / 削除時期明記
4. `tests/test_mcp_server.py` の protocol assertion 更新

## データ互換性

### `.forgewise/audit.jsonl`

JSONL append-only log. schema 変更時:

| 変更タイプ | 互換性 | 対応 |
|---|---|---|
| 新規 field 追加 (optional) | backward compatible | 無対応 (既存 reader が unknown field 無視) |
| 既存 field rename | breaking | 自動マイグレーションスクリプト + 本文書ガイド |
| 既存 field 削除 | breaking | 自動マイグレーションスクリプト + deprecation 1 release |

自動マイグレーションスクリプトは `tools/migrate-audit.py` (現在未作成、vN+1 で
breaking change 発生時に追加)。

### `.secrets.baseline`

`detect-secrets` の baseline. ForgeWise バージョンと独立. tool バージョン upgrade 時:

```bash
uv tool upgrade detect-secrets
uv run detect-secrets scan --baseline .secrets.baseline
```

## ダウングレード

ForgeWise は*公式にダウングレードをサポートしません*。`0.x` の間は audit log /
secrets baseline の forward-only マイグレーションのみ保証。

緊急時:

1. 以前のバージョンを `pip install forgewise==<old_version>` (PyPI 公開後)
2. `.forgewise/audit.jsonl` バックアップ後、新規行を削除 (manual)
3. issue 登録 + ダウングレード理由明記

## 次のステップ

- インストール: `docs/installation.md`
- 環境設定: `docs/configuration.md`
- API カタログ: `docs/api-reference.md`
- 変更履歴: `CHANGELOG.md`
