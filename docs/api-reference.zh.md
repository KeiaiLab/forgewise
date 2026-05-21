# API 参考 — MCP tool

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> [English](api-reference.md) | [한국어](api-reference.ko.md) | [日本語](api-reference.ja.md) | **中文**

ForgeWise 0.1.0 的 33 种 MCP tool 目录. 所有信息以 `forgewise/tools.py` 的
`list_tool_definitions()` 为 SSOT. 本文档为*文档化副本*,新增 tool /
schema 变更时本文档 + `tests/test_mcp_server.py` + `docs/design.md` 必须同步
更新 (CONTRIBUTING.md "Adding a New MCP Tool" 策略).

## 共通事项

### 输入 schema 共通 property

| Property | Type | Required | 说明 |
|---|---|---|---|
| `repo` | string | optional | 仓库根目录路径. 省略时使用服务器默认路径. 但 `get_mcp_server_version` 等部分 tool 是 `accepts_repo: false` |

### GitLab compat tool 追加共通 property

调用 GitLab API 的所有 tool 的 input schema 都包含以下共通 property:

| Property | Type | Required | 说明 |
|---|---|---|---|
| `gitlab_base_url` | string | optional | GitLab base URL. 默认值 = `GITLAB_BASE_URL` 环境变量或 `https://gitlab.com` |
| `gitlab_token` | string | optional | GitLab API token. 默认值 = `GITLAB_TOKEN` 环境变量 |
| `gitlab_timeout` | number | optional | GitLab API timeout (秒) |

### 输出格式

所有 tool 的响应都是 MCP 标准:

```json
{
  "content": [
    {"type": "text", "text": "<JSON string of structured data>"}
  ],
  "structuredContent": {<same JSON as above>}
}
```

`structuredContent` 因 tool 而异 schema 不同. 参见本文档每个 tool entry 的 "output"
段落.

### Annotations

| Annotation | 含义 |
|---|---|
| `readOnlyHint: true` | tool 调用不改变外部状态 |
| `readOnlyHint: false` | 变更类 tool. 需要 `FORGEWISE_ENABLE_MUTATIONS=1` |
| `destructiveHint: false` | 明确非破坏性 |
| `openWorldHint: true` | 可能改变外部系统 (GitLab) 的状态 |

---

## Category A — GitLab Duo Enterprise 对应 (18 种,全部 local)

### 1. `code_suggestions`

**用途**: 返回整个仓库的代码改进候选 (refactor / security finding) 结构化结果.

**input schema**: (无必填项,`repo` optional)

**output (structured)**:
```json
{"suggestions": [{"file": "...", "kind": "refactor|security", "message": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:64` + `forgewise/features.py:ForgeWise.code_suggestions`

---

### 2. `duo_chat`

**用途**: 搜索与问题 token 相关的本地文件,返回上下文.

**input schema**:
- `question` (string, required): 问题

**output (structured)**:
```json
{"question": "...", "matches": [{"file": "...", "snippet": "..."}]}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:69`

---

### 3. `code_explanation` (alias)

**用途**: 文件或行范围解释 — 兼容 alias (实际为 `code_explanation_ide`).

**input schema**:
- `path` (string, required): 相对于仓库根的文件路径
- `start` (integer, optional): 起始行 (1 以上)
- `end` (integer, optional): 结束行 (1 以上)

**output (structured)**:
```json
{"path": "...", "symbols": [...], "slice": "..."}
```

**Annotations**: `readOnlyHint: true`

**Source**: `forgewise/tools.py:77`

---

### 4. `code_explanation_ide`

**用途**: 对应 IDE 代码解释行 — 文件/行范围 + symbol 摘要 + slice.

**input schema**: 与 `code_explanation` 相同 (`path` required, `start` / `end` optional).

**output (structured)**: 与 `code_explanation` 相同.

**Source**: `forgewise/tools.py:83`

---

### 5. `code_explanation_gitlab_ui`

**用途**: GitLab UI 上下文用代码解释.

**input schema**: 与 `code_explanation` 相同.

**output (structured)**: 与 `code_explanation` 相同.

**Source**: `forgewise/tools.py:90`

---

### 6. `refactor_code`

**用途**: 返回长函数 / 长行 / broad exception 等重构候选.

**input schema**:
- `path` (string, required): 文件路径
- `start` / `end` (integer, optional): 行范围

**output (structured)**:
```json
{"path": "...", "candidates": [{"line": 42, "kind": "long_function", "message": "..."}]}
```

**Source**: `forgewise/tools.py:97`

---

### 7. `fix_code`

**用途**: 基于安全 finding 提议可自动修复的危险候选.

**input schema**: 与 `refactor_code` 相同.

**output (structured)**:
```json
{"path": "...", "fixes": [{"line": 42, "finding": "...", "suggestion": "..."}]}
```

**Source**: `forgewise/tools.py:104`

---

### 8. `test_generation`

**用途**: 为 Python 函数生成 `pytest` skeleton.

**input schema**: 与 `refactor_code` 相同.

**output (structured)**:
```json
{"path": "...", "skeletons": [{"function": "...", "test_source": "..."}]}
```

**Source**: `forgewise/tools.py:111`

---

### 9. `code_review`

**用途**: 对整个仓库进行安全 + 可维护性审查. finding 汇总.

**input schema**: (无必填项)

**output (structured)**:
```json
{"findings": [...], "severity_summary": {"high": 2, "medium": 5, "low": 10}}
```

**Source**: `forgewise/tools.py:118`

---

### 10. `root_cause_analysis`

**用途**: 从堆栈跟踪 / 日志中提取原因候选文件/行 + 最后错误.

**input schema**:
- `log` (string, required): 日志路径或日志本文

**output (structured)**:
```json
{"final_error": "...", "candidates": [{"file": "...", "line": 42}]}
```

**Source**: `forgewise/tools.py:124`

---

### 11. `vulnerability_explanation`

**用途**: 解释漏洞模式 (`eval`, `shell=True`, hardcoded secret 等).

**input schema**: 与 `refactor_code` 相同 (`path` + 可选行).

**output (structured)**:
```json
{"path": "...", "vulnerabilities": [{"line": 42, "pattern": "eval", "explanation": "..."}]}
```

**Source**: `forgewise/tools.py:131`

---

### 12. `vulnerability_resolution`

**用途**: 针对发现的漏洞模式给出安全修复方向.

**input schema**: 与 `refactor_code` 相同.

**output (structured)**:
```json
{"path": "...", "resolutions": [{"line": 42, "pattern": "eval", "fix": "..."}]}
```

**Source**: `forgewise/tools.py:138`

---

### 13. `merge_request_summary`

**用途**: 将 `git diff --stat` 统计转为 MR 摘要.

**input schema**:
- `base` (string, optional): 比较基准 ref. 默认值 = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "files_changed": 5, "summary": "..."}
```

**Source**: `forgewise/tools.py:145`

---

### 14. `merge_commit_message_generation`

**用途**: 将 `git diff` 统计转为 merge commit message 草稿.

**input schema**:
- `base` (string, optional): 比较基准 ref. 默认值 = `HEAD~1`

**output (structured)**:
```json
{"base": "HEAD~1", "message": "feat: ..."}
```

**Source**: `forgewise/tools.py:151`

---

### 15. `code_review_summary`

**用途**: 汇总代码审查 finding 数 + severity.

**input schema**: (无必填项)

**output (structured)**:
```json
{"total_findings": 17, "severity_summary": {...}, "top_files": [...]}
```

**Source**: `forgewise/tools.py:157`

---

### 16. `issue_description_generation`

**用途**: 将 prompt 转为 issue 本文 + acceptance criteria.

**input schema**:
- `prompt` (string, required): issue prompt

**output (structured)**:
```json
{"title": "...", "description": "...", "acceptance_criteria": [...]}
```

**Source**: `forgewise/tools.py:163`

---

### 17. `discussion_summary`

**用途**: 讨论文本摘要 — 行数、关键行、问题提取.

**input schema**:
- `text` (string, required): 讨论本文

**output (structured)**:
```json
{"line_count": 42, "key_lines": [...], "questions": [...]}
```

**Source**: `forgewise/tools.py:170`

---

### 18. `sdlc_trends`

**用途**: 汇总仓库的语言分布 + 质量 finding 数.

**input schema**: (无必填项)

**output (structured)**:
```json
{"languages": {"Python": 0.85, "Markdown": 0.10, ...}, "finding_count": 17}
```

**Source**: `forgewise/tools.py:177`

---

## Category B — GitLab MCP compatible (15 种,GitLab API proxy)

> 所有 tool 都额外接受共通的 `gitlab_base_url` / `gitlab_token` / `gitlab_timeout` property.
> 变更类 tool 需要 `FORGEWISE_ENABLE_MUTATIONS=1` (星号表示).

### 19. `get_mcp_server_version`

**用途**: 返回 ForgeWise MCP 服务器 version / protocol / transport.

**input schema**: (无 — `accepts_repo: false`)

**output (structured)**:
```json
{"name": "forgewise", "version": "0.1.0", "protocols": ["2025-03-26", "2025-06-18"]}
```

**Source**: `forgewise/tools.py:183`

---

### 20. `create_issue` ***(变更类)***

**用途**: 新创建 GitLab issue.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `title` (string, required): issue 标题
- `description` (string, optional): issue 描述

**output (structured)**: GitLab API `/projects/:id/issues` POST 响应.

**Source**: `forgewise/tools.py:190`

---

### 21. `get_issue`

**用途**: 查询 GitLab issue.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `issue_iid` (integer, required): issue IID

**output (structured)**: GitLab API `/projects/:id/issues/:iid` GET 响应.

**Source**: `forgewise/tools.py:202`

---

### 22. `create_merge_request` ***(变更类)***

**用途**: 新创建 GitLab MR.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `title` (string, required): MR 标题
- `source_branch` (string, required): source branch
- `target_branch` (string, required): target branch
- `description` (string, optional): MR 描述

**output (structured)**: GitLab API `/projects/:id/merge_requests` POST 响应.

**Source**: `forgewise/tools.py:212`

---

### 23. `get_merge_request`

**用途**: 查询 GitLab MR.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `merge_request_iid` (integer, required): MR IID

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid` GET 响应.

**Source**: `forgewise/tools.py:226`

---

### 24. `get_merge_request_commits`

**用途**: 查询 MR commit 列表.

**input schema**: 与 `get_merge_request` 相同.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/commits` GET 响应.

**Source**: `forgewise/tools.py:236`

---

### 25. `get_merge_request_diffs`

**用途**: 查询 MR diff 列表.

**input schema**: 与 `get_merge_request` 相同.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/diffs` GET 响应.

**Source**: `forgewise/tools.py:246`

---

### 26. `get_merge_request_pipelines`

**用途**: 查询 MR pipeline 列表.

**input schema**: 与 `get_merge_request` 相同.

**output (structured)**: GitLab API `/projects/:id/merge_requests/:iid/pipelines` GET 响应.

**Source**: `forgewise/tools.py:256`

---

### 27. `get_pipeline_jobs`

**用途**: 查询 Pipeline job 列表.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `pipeline_id` (integer, required): Pipeline ID

**output (structured)**: GitLab API `/projects/:id/pipelines/:pid/jobs` GET 响应.

**Source**: `forgewise/tools.py:266`

---

### 28. `manage_pipeline` ***(变更类,`operation != "list"` 时)***

**用途**: Pipeline list / create / retry / cancel.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `operation` (string, required): `list` / `create` / `retry` / `cancel`
- `pipeline_id` (integer, optional): Pipeline ID (`retry`, `cancel` 时需要)
- `ref` (string, optional): branch 或 tag ref (`create` 时需要)
- `variables` (object, optional): pipeline variable (key→string value)

**output (structured)**: 不同 operation 对应的 GitLab API 响应.

**Note**: `operation == "list"` 为 read-only — 绕过 mutation gate.

**Source**: `forgewise/tools.py:276`

---

### 29. `create_workitem_note` ***(变更类)***

**用途**: 新增 Work item (issue, epic, task) 的 note (comment).

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `work_item_iid` (integer, required): Work item IID
- `body` (string, required): note 本文

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` POST 响应.

**Source**: `forgewise/tools.py:290`

---

### 30. `get_workitem_notes`

**用途**: 查询 Work item note 列表.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `work_item_iid` (integer, required): Work item IID

**output (structured)**: GitLab API `/projects/:id/work_items/:iid/notes` GET 响应.

**Source**: `forgewise/tools.py:302`

---

### 31. `search`

**用途**: 调用 GitLab search API.

**input schema**:
- `scope` (string, required): 搜索 scope (`blobs`, `projects`, `merge_requests`, `issues`, `users` 等)
- `search` (string, required): 搜索词
- `id` (string, optional): 项目 ID 或 full path (project-level search)
- `group_id` (string, optional): 组 ID 或 full path (group-level search)

**output (structured)**: GitLab API search 响应.

**Source**: `forgewise/tools.py:312`

---

### 32. `search_labels`

**用途**: GitLab label 搜索.

**input schema**:
- `search` (string, optional): 搜索词 (省略时为全部 label)
- `id` (string, optional): 项目 ID
- `group_id` (string, optional): 组 ID

**output (structured)**: GitLab API label 响应.

**Source**: `forgewise/tools.py:324`

---

### 33. `semantic_code_search`

**用途**: 调用 GitLab semantic code search.

**input schema**:
- `id` (string, required): 项目 ID 或 full path
- `query` (string, required): 搜索查询

**output (structured)**: GitLab API semantic search 响应.

**Source**: `forgewise/tools.py:334`

---

## 调用示例

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

## 下一步

- 安装: `docs/installation.md`
- 环境配置: `docs/configuration.md`
- 版本迁移: `docs/upgrade.md`
- 设计上下文: `docs/design.md`
- 安全策略: `docs/security.md` + `SECURITY.md`
