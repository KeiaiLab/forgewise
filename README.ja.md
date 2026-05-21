# ForgeWise

> [English](README.md) | [한국어](README.ko.md) | **日本語** | [中文](README.zh.md) (placeholder)

ForgeWise は、GitLab Duo Enterprise クラスの開発支援機能を、オープンソース、ローカル実行可能、MCP-native のツール表面として実装する `keiailab` プロジェクトです。

## 命名

選定された名称は **ForgeWise** です。

- **Forge**: すべてのコードフォージ — GitLab、GitHub、Gitea、Forgejo を対象とします。
- **Wise**: 単なるチャットボットではなく、コード解説、レビュー、セキュリティ解説、原因分析、テスト生成、変更要約を、同一のポリシーと監査ログのもとで実行します。
- GitLab Duo の商標を直接利用することを避け、機能互換の表面のみをオープンソースで提供します。

CLI コマンドは `forgewise`、stdio MCP サーバーコマンドは `forgewise-mcp`、HTTP MCP サーバーコマンドは `forgewise-http` です。

## 機能表面

現行 MVP は、外部 LLM 呼び出しなしの決定論的な解析として動作します。同じ API 表面は、社内 LLM や self-hosted モデルルーターを後付けできるよう設計されています。

| ForgeWise ツール | 機能グループ |
| --- | --- |
| `code_suggestions` | コード提案 |
| `duo_chat` | リポジトリコンテキスト Chat |
| `code_explanation` | コード解説互換エイリアス |
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
| `discussion_summary` | ディスカッション要約 |
| `sdlc_trends` | SDLC 品質トレンド |
| `merge_commit_message_generation` | マージコミットメッセージ生成 |
| `code_review_summary` | コードレビュー要約 |
| `issue_description_generation` | Issue 説明生成 |

GitLab MCP サーバー互換のツールも提供します。

| ForgeWise ツール | 対応する GitLab MCP 機能 |
| --- | --- |
| `get_mcp_server_version` | MCP サーバーバージョン |
| `create_issue`、`get_issue` | Issue 作成 / 取得 |
| `create_merge_request`、`get_merge_request` | MR 作成 / 取得 |
| `get_merge_request_commits`、`get_merge_request_diffs` | MR コミット / 差分 |
| `get_merge_request_pipelines`、`get_pipeline_jobs`、`manage_pipeline` | Pipeline 照会 / 管理 |
| `create_workitem_note`、`get_workitem_notes` | Work item ノート作成 / 取得 |
| `search`、`search_labels`、`semantic_code_search` | GitLab 検索 |

## インストール

```bash
uv run --python 3.11 --extra dev python -m pytest
```

開発用インストール:

```bash
uv sync --python 3.11 --extra dev
uv run forgewise --repo . review
```

## CLI の例

```bash
forgewise --repo . explain forgewise/features.py
forgewise --repo . explain-ide forgewise/features.py
forgewise --repo . explain-ui forgewise/features.py
forgewise --repo . vuln-explain forgewise/security.py
forgewise --repo . test-generate forgewise/features.py
forgewise --repo . issue-description "login failure after deploy"
forgewise --repo . check
```

`check` は、セキュリティもしくはメンテナビリティ上の検出事項があれば終了コード `1` で終了します。

## MCP サーバー

MCP クライアントに stdio サーバーとして登録します:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp"
    }
  }
}
```

ツール呼び出しごとに、ツール名、引数、機能名を `.forgewise/audit.jsonl` に記録します。キー名が秘密情報に見える引数は、記録の前に `[REDACTED]` でマスクされます。

GitLab MCP 互換の HTTP エンドポイントは次のように起動します:

```bash
forgewise-http --repo . --host 127.0.0.1 --port 8080 --require-oauth
```

HTTP エンドポイント:

- `POST /api/v4/mcp`: MCP JSON-RPC エンドポイント
- `POST /oauth/register`: Dynamic Client Registration
- `GET /oauth/authorize`: 認可コード発行
- `POST /oauth/token`: アクセストークン交換
- `GET /.well-known/oauth-authorization-server`: OAuth メタデータ

GitLab API ツールは `GITLAB_BASE_URL` と `GITLAB_TOKEN` を利用します。変更を伴うツールはデフォルトで無効化されており、有効化には `FORGEWISE_ENABLE_MUTATIONS=1` が必要です。

## ローカルゲート

GitHub Actions は使用しません。すべての検証はローカルゲートを通じて実行されます。

```bash
make check
```

ゲートの構成:

- `make lint`: `ruff check .`
- `make typecheck`: `mypy forgewise tests`
- `make test`: `python -m pytest`

オプションのライブスモーク:

```bash
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=group/project make smoke-gitlab
```

トークンとプロジェクトが指定されていない場合、スモークはスキップとして終了します。

詳細な設計は [docs/design.md](docs/design.md) を、根拠となる参照は [docs/references.md](docs/references.md) を、セキュリティ運用基準は [docs/security.md](docs/security.md) を参照してください。

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
