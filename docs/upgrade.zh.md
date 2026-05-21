# 升级指南 (Upgrade Guide)

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> [English](upgrade.md) | [한국어](upgrade.ko.md) | [日本語](upgrade.ja.md) | **中文**

ForgeWise 的版本迁移指南. SemVer 策略 + 未来版本兼容性.

## SemVer 策略

ForgeWise 遵循 [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).

| 阶段 | 策略 |
|---|---|
| `0.x.y` (alpha — 当前) | minor (`y` → `y+1`) 也允许 breaking change. 所有 breaking change 都需在 `CHANGELOG.md` 的 `### Changed` 或 `### Removed` 段落 + 本文档迁移指南中添加. |
| `1.0.0` 之后 | 严格 SemVer. MAJOR = breaking, MINOR = additive, PATCH = bug fix. |

## 当前版本

| Stream | 版本 | 状态 |
|---|---|---|
| `main` | `0.1.0` + Unreleased | 活跃 |

`CHANGELOG.md` 的 `[Unreleased]` 段落是下一次发布候选变更的 SSOT.

## 迁移指南

### vN/A → v0.1.0 (initial release)

**当前 initial release 准备中**. 无单独迁移步骤.

安装参见 `docs/installation.md`.

### v0.1.0 → v0.2.0 (placeholder)

(将来 v0.2.0 release 时编写. 格式示例:)

#### Breaking changes

(示例)
- 引入 `forgewise.policy.json` 组织策略文件 — 不存在时使用默认策略
- 新增环境变量 `FORGEWISE_OAUTH_CLIENT_ID` 必填 (HTTP transport + OAuth)
- MCP tool `<tool_name>` 的 input schema 添加 `<param>` (required)

#### 迁移步骤

(示例)
1. 编写 `forgewise.policy.json` (template: `docs/policy-template.json`)
2. 在 `.env` 添加 `FORGEWISE_OAUTH_CLIENT_ID`
3. 在 MCP client 的 `<tool_name>` 调用 site 添加 `<param>`
4. `make check` + `forgewise --repo . check` 回归验证

#### 环境变量映射

| v0.1.0 | v0.2.0 | 备注 |
|---|---|---|
| `<old_var>` | `<new_var>` | (示例) rename — 现有变量保留 1 release 周期作为 deprecated alias |

#### MCP tool 名称映射

| v0.1.0 | v0.2.0 | 备注 |
|---|---|---|
| `<old_tool>` | `<new_tool>` | (示例) rename — alias 保留 1 release |

### vN → vN+1 (general template)

新 minor / major release 时添加本段落:

```markdown
### v<old> → v<new> (<release date>)

#### Breaking changes
- ...

#### 迁移步骤
1. ...

#### 环境变量映射
| <old> | <new> | 备注 |

#### MCP tool 名称映射
| <old> | <new> | 备注 |

#### 数据兼容性
- `.forgewise/audit.jsonl` 格式变更时,自动迁移脚本规范
- 其他持久数据 (DB, cache) 迁移
```

## 依赖更新

`uv.lock` 是 SSOT. 依赖更新:

```bash
# 所有依赖更新到 latest compatible
uv sync --upgrade

# 回归验证
make check

# 检查差异
git diff uv.lock pyproject.toml

# 无变更则 commit,有回归则只 restore lockfile:
# git checkout uv.lock pyproject.toml
```

发生 major version bump 的 dependency 在 PR body 中注明 `<dep>: vN → vN+1`.
怀疑发生 breaking change 的 dep (uvicorn / fastapi / authlib / httpx) 分离到独立 PR
隔离回归风险.

## MCP protocol 更新

ForgeWise 协商以下 MCP protocol version (`forgewise/mcp_server.py` 的
`initialize` 响应):

- `2025-03-26` (legacy)
- `2025-06-18` (current)

引入新 protocol spec 时:

1. 更新 `forgewise/mcp_server.py` 的 `_NEGOTIATED_PROTOCOL_VERSIONS`
2. 将新 spec 的 capability 差异以迁移指南添加到本文档
3. 注明 legacy protocol 支持 deprecate / 删除时点
4. 更新 `tests/test_mcp_server.py` 的 protocol assertion

## 数据兼容性

### `.forgewise/audit.jsonl`

JSONL append-only log. schema 变更时:

| 变更类型 | 兼容性 | 对应 |
|---|---|---|
| 新增 field (optional) | backward compatible | 无对应 (现有 reader 忽略 unknown field) |
| 现有 field rename | breaking | 自动迁移脚本 + 本文档指南 |
| 现有 field 删除 | breaking | 自动迁移脚本 + deprecation 1 release |

自动迁移脚本是 `tools/migrate-audit.py` (当前未编写,vN+1 发生 breaking change 时
添加).

### `.secrets.baseline`

`detect-secrets` 的 baseline. 与 ForgeWise 版本独立. tool 版本 upgrade 时:

```bash
uv tool upgrade detect-secrets
uv run detect-secrets scan --baseline .secrets.baseline
```

## 降级

ForgeWise *官方不支持降级*. 在 `0.x` 期间只保证 audit log /
secrets baseline 的 forward-only 迁移.

紧急情况:

1. `pip install forgewise==<old_version>` 安装早期版本 (PyPI 发布后)
2. backup `.forgewise/audit.jsonl` 后删除新行 (manual)
3. 提交 issue + 注明降级原因

## 下一步

- 安装: `docs/installation.md`
- 环境配置: `docs/configuration.md`
- API 目录: `docs/api-reference.md`
- 变更历史: `CHANGELOG.md`
