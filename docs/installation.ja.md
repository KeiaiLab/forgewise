# インストール (Installation)

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> [English](installation.md) | [한국어](installation.ko.md) | **日本語** | [中文](installation.zh.md)

ForgeWise は Python 3.11+ ベースの MCP-native developer intelligence サーバーです。本文書は
インストール / 環境設定 / 検証 / トラブルシューティングを扱います。

## システム要件

| 項目 | 最小 | 推奨 |
|---|---|---|
| Python | 3.11 | 3.11 または 3.12 |
| `uv` | 0.4 | 0.5+ |
| ディスク | 50 MB | 200 MB (開発 + キャッシュ) |
| OS | Linux / macOS | Linux x86_64 (運用) |
| Memory | 256 MB | 1 GB (大規模リポジトリ分析時) |

`pip` 単独環境もサポートされますが、`uv` が推奨されます (lockfile 一貫性、ビルド速度)。

## クイックインストール

### Option 1 — `uv` (推奨)

開発用 (リポジトリ clone):

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
uv sync --extra dev
```

デプロイ用 (PyPI 公開後、現在 unreleased):

```bash
uv tool install forgewise
```

### Option 2 — `pip`

開発用:

```bash
git clone https://github.com/keiailab/forgewise.git
cd forgewise
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

デプロイ用 (PyPI 公開後):

```bash
pip install forgewise
```

## 環境変数

ForgeWise のランタイム動作は以下の環境変数で制御します。**アスタリスク (*)** は運用環境で必須。

| 変数 | 必須? | デフォルト値 | 説明 |
|---|---|---|---|
| `GITLAB_BASE_URL` | * | `https://gitlab.com` | GitLab CE/EE インスタンス URL (例: `https://gitlab.example.com`) |
| `GITLAB_TOKEN` | * | (なし) | GitLab API token (Personal Access Token または Project Access Token) |
| `FORGEWISE_ENABLE_MUTATIONS` | no | (未設定) | `1` に設定すると変更系 tool (`create_issue`, `create_merge_request`, `manage_pipeline`, `create_workitem_note`) を許可。未設定時はブロック。 |
| `FORGEWISE_REQUIRE_OAUTH` | no | (未設定) | HTTP transport で OAuth 2.0 認証を強制。運用環境では `1` 推奨。 |
| `FORGEWISE_LIVE_GITLAB_TOKEN` | no | (なし) | `make smoke-gitlab` 用の別 token (テスト環境隔離) |
| `FORGEWISE_LIVE_PROJECT_ID` | no | (なし) | `make smoke-gitlab` のテスト対象 project ID または full path |

### OAuth 2.0 応用変数 (HTTP transport)

| 変数 | 必須? | 説明 |
|---|---|---|
| `FORGEWISE_OAUTH_CLIENT_ID` | yes (HTTP + OAuth) | OAuth 2.0 client ID (Dynamic Client Registration 使用時に自動発行) |
| `FORGEWISE_OAUTH_CLIENT_SECRET` | yes (HTTP + OAuth) | OAuth 2.0 client secret. `.env` または secret manager で注入。**commit 絶対禁止。** |
| `FORGEWISE_LOG_LEVEL` | no | `DEBUG` / `INFO` (デフォルト) / `WARN` / `ERROR` |

### `.env` 形式例

```bash
# .env (絶対 commit 禁止 — .gitignore に含める)
GITLAB_BASE_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
FORGEWISE_ENABLE_MUTATIONS=
FORGEWISE_REQUIRE_OAUTH=1
FORGEWISE_OAUTH_CLIENT_ID=forgewise-prod
FORGEWISE_OAUTH_CLIENT_SECRET=...
FORGEWISE_LOG_LEVEL=INFO
```

## 検証

インストール直後に以下のコマンドで環境を検証:

```bash
# 1. CLI 動作確認
forgewise --version
forgewise --repo . check

# 2. MCP stdio transport 起動 (Ctrl+C で終了)
forgewise-mcp

# 3. MCP HTTP transport 起動 (別 shell、Ctrl+C で終了)
forgewise-http --host 127.0.0.1 --port 8080

# 4. ローカルゲート (開発環境)
make check

# 5. GitLab live smoke (オプション、GITLAB_TOKEN + FORGEWISE_LIVE_PROJECT_ID 必要)
FORGEWISE_LIVE_GITLAB_TOKEN=... FORGEWISE_LIVE_PROJECT_ID=keiailab/forgewise make smoke-gitlab
```

すべて zero exit code なら環境は正常。`make check` は ruff + mypy + pytest 543 LOC を検証します。

## トラブルシューティング

### OAuth 認証失敗

症状: HTTP transport `/api/v4/mcp` 呼び出し時 `401 Unauthorized`。

原因 / 対応:

1. `FORGEWISE_REQUIRE_OAUTH=1` だが client が token を渡していない → `Authorization:
   Bearer <access_token>` header 確認。
2. token 期限切れ (デフォルト 1 時間) → `/oauth/token` 再リクエスト。
3. redirect URI が許可されていない → `https://` / `127.0.0.1` / `localhost` のみ許可。
   他のスキームは client 登録自体を拒否。
4. PKCE code_verifier の不一致 → `S256` の場合 base64url(SHA-256(verifier)) 検証確認。

詳細は `docs/security.md` の OAuth セクション参照。

### GitLab 接続失敗

症状: `GitLab API 호출 실패: HTTP 401` または `Connection refused`。

原因 / 対応:

1. `GITLAB_TOKEN` 未設定 → `.env` 確認 + `source .env` またはプロセスマネージャの
   env 注入確認。
2. token 権限不足 → `read_repository` + `read_api` 最小限。変更系 tool 使用時は
   `api` scope 必要。
3. `GITLAB_BASE_URL` の誤字 → `https://` 含む、trailing slash なし推奨。
4. self-signed cert → `httpx` の `verify=False` 回避は**禁止**。社内 CA chain を
   システム trust store に登録。
5. network proxy → `HTTPS_PROXY` / `HTTP_PROXY` 環境変数の正常設定確認。

### Python バージョン不一致

症状: `python: command not found` または `Python 3.10 detected, requires >= 3.11`。

対応:

```bash
# uv 使用時は自動分離された Python
uv python install 3.11

# または pyenv
pyenv install 3.11.10
pyenv local 3.11.10
```

`Makefile` の `PYTHON ?= 3.11` override 可能: `make check PYTHON=3.12`。

### mypy strict 失敗

症状: `make check` の typecheck 段階で `Function is missing a type annotation`。

対応: `pyproject.toml` の `[tool.mypy] strict = true` + `disallow_untyped_defs =
true` が SSOT。新規コードはすべての関数 signature に type annotation 必須。
`# type: ignore[<code>]` 回避は PR body に理由明記。

### lefthook hook 非活性

症状: `git commit` 時の hook 出力 0。

対応:

```bash
# hook インストール確認
ls -la .git/hooks/pre-commit .git/hooks/pre-push .git/hooks/commit-msg

# 未インストール時
make setup-hooks
```

`LEFTHOOK=0 git commit ...` で全体回避可能だが PR 本文に理由明記義務。

## 次のステップ

- 環境設定詳細: `docs/configuration.md`
- 33 種 MCP tool カタログ: `docs/api-reference.md`
- バージョンマイグレーション: `docs/upgrade.md`
- セキュリティポリシー: `docs/security.md` + `SECURITY.md`
- 貢献ガイド: `CONTRIBUTING.md`
