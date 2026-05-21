# API リファレンス — MCP tool

> ⚠️ This translation is AI-generated and pending native review. See [日本語 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ja.md) for terminology.

> [English](api-reference.md) | [한국어](api-reference.ko.md) | **日本語** | [中文](api-reference.zh.md)

ForgeWise 0.1.0 の 33 種 MCP tool カタログ。すべての情報は `forgewise/tools.py` の
`list_tool_definitions()` が SSOT。本文書は*文書化コピー*で、新規 tool 追加 /
schema 変更時に本文書 + `tests/test_mcp_server.py` + `docs/design.md` を同時更新
する義務 (CONTRIBUTING.md "Adding a New MCP Tool" ポリシー)。

## 共通事項

### 入力 schema 共通 property

| Property | Type | Required | 説明 |
|---|---|---|---|
| `repo` | string | optional | リポジトリルートパス。省略時はサーバーデフォルトパス使用。ただし `get_mcp_server_version` 等の一部 tool は `accepts_repo: false` |

### GitLab compat tool 追加共通 property

GitLab API を呼び出すすべての tool の input schema には以下の共通 property が含まれます:

| Property | Type | Required | 説明 |
|---|---|---|---|
| `gitlab_base_url` | string | optional | GitLab base URL. デフォルト = `GITLAB_BASE_URL` 環境変数または `https://gitlab.com` |
| `gitlab_token` | string | optional | GitLab API token. デフォルト = `GITLAB_TOKEN` 環境変数 |
| `gitlab_timeout` | number | optional | GitLab API timeout (秒) |

### 出力形式

すべての tool の応答は MCP 標準:

```json
{
  "content": [
    {"type": "text", "text": "<JSON string of structured data>"}
  ],
  "structuredContent": {<same JSON as above>}
}
```

`structuredContent` は tool 別に schema が異なる。本文書の各 tool entry の "output"
セクション参照。

### Annotations

| Annotation | 意味 |
|---|---|
| `readOnlyHint: true` | tool 呼び出しが外部状態を変更しない |
| `readOnlyHint: false` | 変更系 tool. `FORGEWISE_ENABLE_MUTATIONS=1` 必要 |
| `destructiveHint: false` | 明示的に非破壊的 |
| `openWorldHint: true` | 外部システム (GitLab) の状態変更可能 |

---

## Category A — GitLab Duo Enterprise 対応 (18 種、すべて local)

### 1. `code_suggestions`

**用途**: リポジトリ全体のコード改善候補 (refactor / security finding) を構造化返却。

**input schema**: (必須項目なし、`repo` optional)

**output (structured)**:
```json
{"suggestions": [{"file": "...", "kind": "refactor|security", "message": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:64` + `forgewise/features.py:ForgeWise.code_suggestions`

---

### 2. `duo_chat`

**用途**: 質問トークンに関連するローカルファイルを検索しコンテキスト返却。

**input schema**:
- `question` (string, required): 質問

**output (structured)**:
```json
{"question": "...", "matches": [{"file": "...", "snippet": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:69`

---

### 3. `code_explanation` (alias)

**用途**: ファイルまたはライン範囲解説 — 互換 alias (実際は `code_explanation_ide`)。

**input schema**:
- `path` (string, required): リポジトリルート基準のファイルパス
- `start` (integer, optional): 開始ライン (1 以上)
- `end` (integer, optional): 終了ライン (1 以上)

**output (structured)**:
```json
{"path": "...", "symbols": [...], "slice": "..."}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:77`

---

### 4. `code_explanation_ide`

**用途**: IDE コード解説行に対応 — ファイル/ライン範囲 + symbol 要約 + slice。

**input schema**: `code_explanation` と同じ (`path` required, `start` / `end` optional)。

**output (structured)**: `code_explanation` と同じ。

**Source**: `forgewise/tools.py:83`

---

### 5. `code_explanation_gitlab_ui`

**用途**: GitLab UI コンテキスト用コード解説。

**input schema**: `code_explanation` と同じ。

**output (structured)**: `code_explanation` と同じ。

**Source**: `forgewise/tools.py:90`

---

### 6. `refactor_code`

**用途**: 長い関数 / 長い行 / broad exception 等のリファクタリング候補を返却。

**input schema**:
- `path` (string, required): ファイルパス
- `start` / `end` (integer, optional): ライン範囲

**output (structured)**:
```json
{"path": "...", "candidates": [{"line": 42, "kind": "long_function", "message": "..."}]}
```

**Source**: `forgewise/tools.py:97`

---

### 7. `fix_code`

**用途**: セキュリティ finding ベースで自動修正可能な危険候補を提案。

**input schema**: `refactor_code` と同じ。

**output (structured)**:
```json
{"path": "...", "fixes": [{"line": 42, "finding": "...", "suggestion": "..."}]}
```

**Source**: `forgewise/tools.py:104`

---

### 8. `test_generation`

**用途**: Python 関数に対する `pytest` skeleton 生成。

**input schema**: `refactor_code` と同じ。

**output (structured)**:
```json
{"path": "...", "skeletons": [{"function": "...", "test_source": "..."}]}
```

**Source**: `forgewise/tools.py:111`

---

### 9. `code_review`

**用途**: リポジトリ全体に対するセキュリティ + 保守性レビュー。finding 集計。

**input schema**: (必須項目なし)

**output (structured)**:
```json
{"findings": [...], "severity_summary": {"high": 2, "medium": 5, "low": 10}}
```

**Source**: `forgewise/tools.py:118`

---

### 10. `root_cause_analysis`

**用途**: スタックトレース / ログから原因候補ファイル/ライン + 最終エラーを抽出。

**input schema**:
- `log` (string, required): ログパスまたはログ本文

**output (structured)**:
```json
{"final_error": "...", "candidates": [{"file": "...", "line": 42}]}
```

**Source**: `forgewise/tools.py:124`

---

### 11. `vulnerability_explanation`

**用途**: 脆弱パターン (`eval`, `shell=True`, hardcoded secret 等) 解説。

**input schema**: `refactor_code` と同じ (`path` + 選択ライン)。

**output (structured)**:
```json
{"path": "...", "vulnerabilities": [{"line": 42, "pattern": "eval", "explanation": "..."}]}
```

**Source**: `forgewise/tools.py:131`

---

### 12. `vulnerability_resolution`

**用途**: 発見された脆弱パターン別の安全な修正方向提示。

**input schema**: `refactor_code` と同じ。

**output (structured)**:
```json
{"path": "...", "resolutions": [{"line": 42, "pattern": "eval", "fix": "..."}]}
```

**Source**: `forgewise/tools.py:138`

---

### 13. `merge_request_summary`

**用途**: `git diff --stat` 統計を MR 要約に変換。

**input schema**:
- `base` (string, optional): 比較基準 ref. デフォルト = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "files_changed": 5, "summary": "..."}
```

**Source**: `forgewise/tools.py:145`

---

### 14. `merge_commit_message_generation`

**用途**: `git diff` 統計を merge commit message 草案に変換。

**input schema**:
- `base` (string, optional): 比較基準 ref. デフォルト = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "message": "feat: ..."}
```

**Source**: `forgewise/tools.py:151`

---

### 15. `code_review_summary`

**用途**: コードレビュー finding 数 + severity を要約。

**input schema**: (必須項目なし)

**output (structured)**:
```json
{"total_findings": 17, "severity_summary": {...}, "top_files": [...]}
```

**Source**: `forgewise/tools.py:157`

---

### 16. `issue_description_generation`

**用途**: プロンプトを issue 本文 + acceptance criteria に変換。

**input schema**:
- `prompt` (string, required): issue プロンプト

**output (structured)**:
```json
{"title": "...", "description": "...", "acceptance_criteria": [...]}
```

**Source**: `forgewise/tools.py:163`

---

### 17. `discussion_summary`

**用途**: 議論テキスト要約 — 行数、キー行、質問抽出。

**input schema**:
- `text` (string, required): 議論本文

**output (structured)**:
```json
{"line_count": 42, "key_lines": [...], "questions": [...]}
```

**Source**: `forgewise/tools.py:170`

---

### 18. `sdlc_trends`

**用途**: リポジトリの言語分布 + 品質 finding 数集計。

**input schema**: (必須項目なし)

**output (structured)**:
```json
{"languages": {"Python": 0.85, "Markdown": 0.10, ...}, "finding_count": 17}
```

**Source**: `forgewise/tools.py:177`

---

## Category B — GitLab MCP compatible (15 種、GitLab API proxy)

> すべての tool は共通の `gitlab_base_url` / `gitlab_token` / `gitlab_timeout` property
> を追加で受け取る。変更系 tool は `FORGEWISE_ENABLE_MUTATIONS=1` 必要 (アスタリスク表示)。

### 19. `get_mcp_server_version`

**用途**: ForgeWise MCP サーバー version / protocol / transport 返却。

**input schema**: (なし — `accepts_repo: false`)

**output (structured)**:
```json
{"name": "forgewise", "version": "0.1.0", "protocols": ["2025-03-26", "2025-06-18"]}
```

**Source**: `forgewise/tools.py:183`

---

### 20. `create_issue` ***(変更系)***

**用途**: GitLab issue 新規作成。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `title` (string, required): issue タイトル
- `description` (string, optional): issue 説明

**output (structured)**: GitLab API `/projects/:id/issues` POST 応答。

**Source**: `forgewise/tools.py:190`

---

### 21. `get_issue`

**用途**: GitLab issue 照会。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `issue_iid` (integer, required): issue IID

**output (structured)**: GitLab API `/projects/:id/issues/:iid` GET 応答。

**Source**: `forgewise/tools.py:202`

---

### 22. `create_merge_request` ***(変更系)***

**用途**: GitLab MR 新規作成。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `title` (string, required): MR タイトル
- `source_branch` (string, required): source branch
- `target_branch` (string, required): target branch
- `description` (string, optional): MR 説明

**output (structured)**: GitLab API `/projects/:id/merge_requests` POST 応答。

**Source**: `forgewise/tools.py:212`

---

### 23. `get_merge_request`

**用途**: GitLab MR 照会。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `merge_request_iid` (integer, required): MR IID

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid` GET 応答。

**Source**: `forgewise/tools.py:226`

---

### 24. `get_merge_request_commits`

**用途**: MR commit 一覧照会。

**input schema**: `get_merge_request` と同じ。

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/commits` GET 応答。

**Source**: `forgewise/tools.py:236`

---

### 25. `get_merge_request_diffs`

**用途**: MR diff 一覧照会。

**input schema**: `get_merge_request` と同じ。

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/diffs` GET 応答。

**Source**: `forgewise/tools.py:246`

---

### 26. `get_merge_request_pipelines`

**用途**: MR pipeline 一覧照会。

**input schema**: `get_merge_request` と同じ。

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/pipelines` GET 応答。

**Source**: `forgewise/tools.py:256`

---

### 27. `get_pipeline_jobs`

**用途**: Pipeline job 一覧照会。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `pipeline_id` (integer, required): Pipeline ID

**output (structured)**: GitLab API `/projects/:id/pipelines/:pid/jobs` GET 応答。

**Source**: `forgewise/tools.py:266`

---

### 28. `manage_pipeline` ***(変更系、`operation != "list"` 時)***

**用途**: Pipeline list / create / retry / cancel.

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `operation` (string, required): `list` / `create` / `retry` / `cancel`
- `pipeline_id` (integer, optional): Pipeline ID (`retry`, `cancel` 時に必要)
- `ref` (string, optional): branch または tag ref (`create` 時に必要)
- `variables` (object, optional): pipeline variable (key→string value)

**output (structured)**: operation 別の GitLab API 応答。

**Note**: `operation == "list"` は read-only — mutation gate 迂回。

**Source**: `forgewise/tools.py:276`

---

### 29. `create_workitem_note` ***(変更系)***

**用途**: Work item (issue, epic, task) に note (comment) 新規。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `work_item_iid` (integer, required): Work item IID
- `body` (string, required): note 本文

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` POST 応答。

**Source**: `forgewise/tools.py:290`

---

### 30. `get_workitem_notes`

**用途**: Work item note 一覧照会。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `work_item_iid` (integer, required): Work item IID

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` GET 応答。

**Source**: `forgewise/tools.py:302`

---

### 31. `search`

**用途**: GitLab search API 呼び出し。

**input schema**:
- `scope` (string, required): 検索 scope (`blobs`, `projects`, `merge_requests`, `issues`, `users` 等)
- `search` (string, required): 検索語
- `id` (string, optional): プロジェクト ID または full path (project-level search)
- `group_id` (string, optional): グループ ID または full path (group-level search)

**output (structured)**: GitLab API search 応答。

**Source**: `forgewise/tools.py:312`

---

### 32. `search_labels`

**用途**: GitLab label 検索。

**input schema**:
- `search` (string, optional): 検索語 (省略時は全 label)
- `id` (string, optional): プロジェクト ID
- `group_id` (string, optional): グループ ID

**output (structured)**: GitLab API label 応答。

**Source**: `forgewise/tools.py:324`

---

### 33. `semantic_code_search`

**用途**: GitLab semantic code search 呼び出し。

**input schema**:
- `id` (string, required): プロジェクト ID または full path
- `query` (string, required): 検索クエリ

**output (structured)**: GitLab API semantic search 応答。

**Source**: `forgewise/tools.py:334`

---

## 呼び出し例

### stdio (直接 JSON-RPC)

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "code_review", "arguments": {"repo": "."}}}' | forgewise-mcp
```

### HTTP (curl)

```bash
curl -X POST http://127.0.0.1:8080/api/v4/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <oauth_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "code_review",
      "arguments": {"repo": "."}
    }
  }'
```

### Python client (snippet)

```python
import httpx, json

async with httpx.AsyncClient() as c:
    r = await c.post(
        "http://127.0.0.1:8080/api/v4/mcp",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "code_review", "arguments": {"repo": "."}}
        }
    )
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
```

## 次のステップ

- インストール: `docs/installation.md`
- 環境設定: `docs/configuration.md`
- バージョンマイグレーション: `docs/upgrade.md`
- 設計コンテキスト: `docs/design.md`
- セキュリティポリシー: `docs/security.md` + `SECURITY.md`
