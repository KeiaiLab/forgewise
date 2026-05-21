# ForgeWise

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> [English](README.md) | [한국어](README.ko.md) | **日本語** | [中文](README.zh.md)

ForgeWise は GitLab Duo Enterprise クラスの開発支援機能を、オープンソース、
ローカル実行、MCP-native ツール表面として実装する `keiailab` プロジェクトです。

## 命名

選択名は **ForgeWise** です。

- **Forge**: GitLab、GitHub、Gitea、Forgejo といったすべての code forge を対象とします。
- **Wise**: 単なるチャットボットではなく、コード解説、レビュー、セキュリティ
  解説、原因分析、テスト生成、変更要約を同じポリシーと監査ログのもとで実行します。
- GitLab Duo 商標を直接使用せず、機能互換表面のみをオープンソースで提供します。

CLI コマンドは `forgewise`、stdio MCP サーバーコマンドは `forgewise-mcp`、HTTP
MCP サーバーコマンドは `forgewise-http` です。

## 機能表面

現在の MVP は外部 LLM 呼び出しなしの決定論的分析で動作します。同じ API 表面上に
社内 LLM またはセルフホストモデルルーターを取り付けられるよう設計されています。

| ForgeWise tool | 機能グループ |
| --- | --- |
| `code_suggestions` | コード提案 |
| `duo_chat` | リポジトリコンテキスト Chat |
| `code_explanation` | コード解説互換 alias |
| `code_explanation_ide` | IDE コード解説 |
| `code_explanation_gitlab_ui` | GitLab UI コード解説 |
| `refactor_code` | リファクタリング提案 |
| `fix_code` | 修正提案 |
| `test_generation` | テスト生成 |
| `code_review` | コードレビュー |
| `root_cause_analysis` | 原因分析 |
| `vulnerability_explanation` | 脆弱性解説 |
| `vulnerability_resolution` | 脆弱性解決提案 |
| `merge_request_summary` | MR 要約 |
| `discussion_summary` | 議論要約 |
| `sdlc_trends` | SDLC 品質トレンド |
| `merge_commit_message_generation` | Merge commit メッセージ生成 |
| `code_review_summary` | コードレビュー要約 |
| `issue_description_generation` | Issue 説明生成 |

GitLab MCP server 互換 tool も併せて提供します。

| ForgeWise tool | 対応 GitLab MCP 機能 |
| --- | --- |
| `get_mcp_server_version` | MCP サーバーバージョン |
| `create_issue`, `get_issue` | Issue 作成 / 取得 |
| `create_merge_request`, `get_merge_request` | MR 作成 / 取得 |
| `get_merge_request_commits`, `get_merge_request_diffs` | MR commit / diff |
| `get_merge_request_pipelines`, `get_pipeline_jobs`, `manage_pipeline` | Pipeline 照会 / 管理 |
| `create_workitem_note`, `get_workitem_notes` | Work item note 作成 / 取得 |
| `search`, `search_labels`, `semantic_code_search` | GitLab 検索 |

## インストール

```bash
uv run --python 3.11 --extra dev python -m pytest
```

開発インストール:

```bash
uv sync --python 3.11 --extra dev
uv run forgewise --repo . review
```

## CLI 例

```bash
forgewise --repo . explain forgewise/features.py
forgewise --repo . explain-ide forgewise/features.py
forgewise --repo . explain-ui forgewise/features.py
forgewise --repo . vuln-explain forgewise/security.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . issue-description "デプロイ後のログイン失敗"
forgewise --repo . check
```

`check` はセキュリティまたは保守性 finding が存在する場合 exit code `1` を返します。

## MCP サーバー

MCP クライアントには stdio サーバーとして登録します:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

各 tool 呼び出しは `.forgewise/audit.jsonl` に tool 名、引数、機能名を記録します。
秘密値のように見える引数キーは記録前に `[REDACTED]` でマスキングされます。

GitLab MCP 互換 HTTP エンドポイントは以下のように実行します:

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

HTTP エンドポイント:

- `POST /api/v4/mcp`: MCP JSON-RPC エンドポイント
- `POST /oauth/register`: Dynamic Client Registration
- `GET /oauth/authorize`: authorization code 発行
- `POST /oauth/token`: access token 交換
- `GET /.well-known/oauth-authorization-server`: OAuth metadata

GitLab API tool は `GITLAB_BASE_URL` と `GITLAB_TOKEN` を使用します。変更系 tool は
デフォルトで無効化されており、有効化するには `FORGEWISE_ENABLE_MUTATIONS=1` が必要です。

## ローカルゲート

GitHub Actions は使用しません。すべての検証はローカルゲートで実行されます。

```bash
make check
```

ゲート構成:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

オプションの live smoke:

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=group/project make smoke-gitlab
```

token と project が存在しない場合、smoke は skip として終了します。

詳細な設計は [docs/design.md](docs/design.md)、根拠リファレンスは
[docs/references.md](docs/references.md)、セキュリティ運用基準は
[docs/security.md](docs/security.md) を参照してください。

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
