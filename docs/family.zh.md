<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# keiailab operator family

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> 共享统一治理基线的 5 个 sister 项目 — 基于 `operator-commons` (Go) 的 3 个 Kubernetes 操作器 + 1 个 MCP-native 开发者智能工具 (`forgewise`, Python).

本页面是从 **`forgewise`** 仓库阅读的 family canonical cross-link.

## Family 概览

| 项目 | 语言 | 领域 | 状态 | 仓库 |
|---|---|---|---|---|
| **`postgres-operator`** | Go | Kubernetes 操作器 (PostgreSQL 18+) | active | https://github.com/keiailab/postgres-operator |
| **`mongodb-operator`** | Go | Kubernetes 操作器 (MongoDB 7.0+) | active | https://github.com/keiailab/mongodb-operator |
| **`valkey-operator`** | Go | Kubernetes 操作器 (Valkey 8.0+, Redis fork BSD-3) | active | https://github.com/keiailab/valkey-operator |
| **`operator-commons`** | Go | 3 操作器共享 Go 库 | v0.7.0 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | Python 3.11+ | MCP-native 开发者智能 (GitLab Duo Enterprise 兼容) | active (0.1.x alpha) | https://github.com/keiailab/forgewise |

## 共享策略

所有 5 个项目即使技术栈不同,也收敛到相同的治理 primitive:

- **Apache-2.0** 全栈 — 不使用 SSPL,SaaS 表面不使用著佐权
- **本地 4 层 gate** — pre-commit + pre-push + Makefile + 审阅者证据 (`RFC-0002`, 永久禁用 GitHub Actions)
- **i18n 4-lang** — README + canonical 文档以英文 / 한국어 / 日本語 / 中文 (cleanup supercycle Wave 4, 2026-05-21)
- **DCO + Conventional Commits** — 每个 commit 都需 `Signed-off-by:` + `<type>(<scope>)?: <subject>` 格式
- **韩文 commit message + PR body** — keiailab 治理基线 (`~/.claude/CLAUDE.md` §2)
- **Plan/Spec/ADR 追踪** — 各项目 `docs/plans/` + `docs/specs/` + `docs/kb/adr/`,跨项目治理在 `~/.claude/rfcs/`

## `forgewise` 的独特性

`forgewise` 是 family 中唯一的非 Go 项目。技术栈差异记录在:

| 领域 | Operator family (Go) | `forgewise` (Python) |
|---|---|---|
| 包管理器 | `go mod` | `uv` (SSOT: `pyproject.toml`) |
| Lint | `gofmt + go vet + golangci-lint` | `ruff check + ruff format` |
| 类型检查 | `staticcheck` | `mypy --strict` |
| 测试运行器 | `go test -race ./...` | `pytest -q --strict-markers` |
| Audit | `govulncheck` | `pip-audit` |
| 分发 | Helm chart + OLM bundle | PyPI 包 + 容器镜像 (GHCR, 计划中) |
| 运行时 | Kubernetes controller-runtime | MCP 服务器 (stdio + HTTP/FastAPI/OAuth 2.0 DCR) |

完整偏离理由 + override matrix: `AGENTS.md` (Tier-3 override) + `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md`.

## 禁止策略

- ❌ **用于 release gate 的 GitHub Actions** — 本地 4 层 enforcement (参见 RFC-0002, 事件 I-2026-04-28: GHA billing SPOF)
- ❌ **嵌入 upstream proprietary code** — `forgewise` 仅提供 GitLab Duo Enterprise 的*功能兼容表面*,不包含 Duo 商标 / proprietary code / 模型权重
- ❌ **MVP 中调用外部 LLM** — `forgewise` MVP 是确定性的 (零 LLM 调用),内部 LLM 路由器仅作为 opt-in attach point
- ❌ **Roadmap 中基于时间的截止日期** — 改用功能 checklist + 完成度 %

## 起点 (`forgewise` 特有)

| 任务 | Entry point |
|---|---|
| 安装 + 环境验证 | [docs/installation.md](installation.md) |
| MCP client 配置 + OAuth | [docs/configuration.md](configuration.md) |
| 33 种 MCP tool 目录 | [docs/api-reference.md](api-reference.md) |
| 升级 / 迁移策略 | [docs/upgrade.md](upgrade.md) |
| 设计上下文 | [docs/design.md](design.md) |
| 安全基线 | [docs/security.md](security.md) + [SECURITY.md](../SECURITY.md) |
| Issue / 功能请求 | https://github.com/keiailab/forgewise/issues |
| 设计 / 路线图讨论 | https://github.com/keiailab/forgewise/discussions |
| 代码贡献 | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| 安全问题上报 | [SECURITY.md](../SECURITY.md) |
| 品牌 / 声音 | [BRANDING.md](../BRANDING.md) |
| 发布历史 | [CHANGELOG.md](../CHANGELOG.md) |
| 项目特定 AI override | [AGENTS.md](../AGENTS.md) (Tier-3) |

## Cross-family 兼容性

3 个数据库操作器以相同版本 import `github.com/keiailab/operator-commons` (当前 `v0.7.0+`). `forgewise` *不* import operator-commons (Go ↔ Python 边界),但共享:

- 治理基线 (`~/.claude/CLAUDE.md` Tier-1)
- ADR / RFC / commit 约定
- i18n 策略 (`operator-commons/docs/i18n/README.md` SSOT)
- 术语表 (`operator-commons/docs/i18n/glossary-{ko,ja,zh}.md`)
- pre-commit hook 模式 (lefthook)

`operator-commons` 的 breaking change 要求 3 个 Go 操作器同步 bump — `forgewise` 在 API 边界上不受影响,但可通过 `scripts/sync-from-commons.sh` 获取共享 lefthook / i18n / 治理更新.

## i18n

本页面 (以及所有 `forgewise` canonical 文档) 提供 4 种语言:

- [English](family.md) (canonical)
- [한국어](family.ko.md)
- [日本語](family.ja.md)
- **中文** (本文件)

发生分歧时英文版对技术内容具有权威性 (authoritative); 本地化版本以母语自然反映相同决策.

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
  © 2026 keiailab · <a href="../LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
