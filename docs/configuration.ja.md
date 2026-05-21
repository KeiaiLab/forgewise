# 設定 (Configuration)

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> [English](configuration.md) | [한국어](configuration.ko.md) | **日本語** | [中文](configuration.zh.md)

ForgeWise の運用インターフェイス (MCP client 登録 / OAuth scope / GitLab 認証 /
audit log / mutation gate) をまとめます。環境変数表は `docs/installation.md`
参照。

## MCP client 登録

ForgeWise は 2 種類の transport を提供します。

### stdio transport (`forgewise-mcp`)

ローカル MCP client (Claude Desktop, Cursor, Continue など) と直接通信。追加認証不要
(client がホスト OS の権限で実行)。

Claude Desktop `claude_desktop_config.json` 例:

```json
{
  "mcpServers": {
    "forgewise": {
      "command": "forgewise-mcp",
      "env": {
        "GITLAB_BASE_URL": "https://gitlab.example.com",
        "GITLAB_TOKEN": "glpat-xxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

Cursor `.cursor/mcp.json` 形式も同じ。

### HTTP transport (`forgewise-http`)

リモート MCP client + 多重ユーザー環境。FastAPI + uvicorn + OAuth 2.0 Dynamic Client
Registration。

```bash
forgewise-http --host 127.0.0.1 --port 8080 --require-oauth
```

CLI option:

| Option | デフォルト | 説明 |
|---|---|---|
| `--host` | `127.0.0.1` | bind address. 0.0.0.0 使用時は firewall + reverse proxy 推奨 |
| `--port` | `8080` | bind port |
| `--require-oauth` | (off) | OAuth 2.0 認証強制。運用環境推奨 (`FORGEWISE_REQUIRE_OAUTH=1` と等価) |
| `--workers` | `1` | uvicorn worker 数 (CPU bound ではないので通常 1 で十分) |

MCP endpoint: `POST /api/v4/mcp` (GitLab MCP server 互換 URL)。

## MCP tool input schema ポリシー

すべての 33 種 tool は JSON Schema strict mode です。一般パターン:

```json
{
  "name": "<tool_name>",
  "description": "<日本語説明>",
  "inputSchema": {
    "type": "object",
    "properties": {
      "repo": {"type": "string", "description": "リポジトリルートパス。省略時はサーバーデフォルトパス使用。"},
      "<param>": {"type": "<type>", "description": "<日本語説明>"}
    },
    "required": ["<param>"]
  },
  "annotations": {
    "readOnlyHint": true,
    "destructiveHint": false
  }
}
```

`annotations.readOnlyHint`:

- `true` — すべての read-only tool (Duo 18 種 + GitLab 照会 tool)
- `false` — 変更系 tool. `openWorldHint: true` 付加. `FORGEWISE_ENABLE_MUTATIONS=1`
  必要.

詳細 tool 別 schema は `docs/api-reference.md` 参照。

## OAuth 2.0 scope

ForgeWise の GitLab OAuth 2.0 application に登録する scope:

| Scope | 用途 | 必須? |
|---|---|---|
| `read_repository` | コード分析 (read-only). git clone / file read 同等. | yes |
| `read_api` | GitLab API 照会 (issue / MR / pipeline / search). | yes |
| `api` (write) | 変更系 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`). | **オプション** — `FORGEWISE_ENABLE_MUTATIONS=1` 時のみ必要. 運用環境では別 OAuth application 分離推奨. |

### DCR endpoint

| Endpoint | Method | 用途 |
|---|---|---|
| `/oauth/register` | POST | Dynamic Client Registration. redirect URI 登録. |
| `/oauth/authorize` | GET | Authorization code 発行 (5 分有効) |
| `/oauth/token` | POST | Access token 交換 (1 時間有効) |
| `/oauth/.well-known/oauth-authorization-server` | GET | RFC 8414 metadata |

PKCE: `plain` / `S256` 対応。`S256` 推奨。

Redirect URI 許可パターン:

- `https://*` (TLS 強制)
- `http://127.0.0.1:*` (localhost dev)
- `http://localhost:*` (localhost dev)

他のスキームは client 登録自体を拒否。

## GitLab API 認証

GitLab REST API 呼び出しには token が必要です。ForgeWise は以下の優先順位で token を
resolve:

1. **Tool argument** `gitlab_token` (per-call override)
2. **環境変数** `GITLAB_TOKEN` (サーバー起動時)
3. (なし) → tool 失敗: `필수 인자가 없습니다: gitlab_token`

マスキングポリシー: token は絶対に audit log に記録されません。秘密値キーワード (`token` /
`secret` / `password` / `key`) を含む argument は `[REDACTED]` に自動マスキング。

## audit log

ForgeWise はすべての tool 呼び出しを `.forgewise/audit.jsonl` に記録します。

### 位置

```
<repo_root>/.forgewise/audit.jsonl
```

各行 = 1 JSON object (JSONL)。形式:

```json
{
  "ts": "2026-05-21T10:30:00.000000Z",
  "tool": "code_review",
  "arguments": {"repo": ".", "gitlab_token": "[REDACTED]"},
  "result_summary": {"finding_count": 7, "severity_high": 2}
}
```

### マスキングルール

以下のキーワードを含む argument key は value が `[REDACTED]` に自動置換:

- `token` (例: `gitlab_token`)
- `secret` (例: `client_secret`)
- `password`
- `key` (例: `api_key`)

詳細: `forgewise/audit.py:mask_secrets` 参照。

### ローテーション

ForgeWise は audit log の自動ローテーションを提供しません。logrotate または cron job で
定期的に archive を推奨 (例: 週 1 回、gzip 圧縮)。

## mutation gate

`FORGEWISE_ENABLE_MUTATIONS=1` 未設定時、以下の tool は呼び出しがブロックされます:

| Tool | 影響 |
|---|---|
| `create_issue` | GitLab issue 新規作成 |
| `create_merge_request` | GitLab MR 新規作成 |
| `manage_pipeline` (`operation != list`) | pipeline create / retry / cancel |
| `create_workitem_note` | Work item note 新規 |

ブロック時 error message: `변경성 GitLab tool은 FORGEWISE_ENABLE_MUTATIONS=1일 때만
실행됩니다.`

運用環境では*読み取り専用* MCP application と*書き込み可能* MCP application を分離
デプロイし、OAuth scope + `FORGEWISE_ENABLE_MUTATIONS` 環境変数を別々に管理することを推奨。

## smoke-gitlab 活用

`make smoke-gitlab` は live GitLab インスタンスに対し read-only tool subset を呼び出して
接続性 + 権限を検証します。CI 不在環境の*第 4 層 (手動ゲート)*。

```bash
export FORGEWISE_LIVE_GITLAB_TOKEN=glpat-xxx
export FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise
make smoke-gitlab
```

出力例:

```
== ForgeWise GitLab smoke test ==
[1/5] get_mcp_server_version ... OK (version: 0.1.0)
[2/5] get_issue (#1) ... OK
[3/5] search (scope=blobs, search='ForgeWise') ... OK (5 hits)
[4/5] search_labels ... OK (12 labels)
[5/5] get_merge_request_commits (!1) ... OK (3 commits)
PASS
```

変更系 tool は smoke に含まれません (運用環境への副作用回避)。

## 分析結果 — tool カウント

ForgeWise 0.1.0 は合計 **33 種 MCP tool** を提供:

- **18 種 GitLab Duo Enterprise 対応** (すべて local、外部 LLM 呼び出しなし)
- **15 種 GitLab MCP compatible** (GitLab API proxy)

詳細カタログは `docs/api-reference.md` 参照。

## 次のステップ

- インストール: `docs/installation.md`
- API カタログ: `docs/api-reference.md`
- バージョンマイグレーション: `docs/upgrade.md`
- セキュリティポリシー: `docs/security.md` + `SECURITY.md`
