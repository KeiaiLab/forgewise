# 品牌指南 — `forgewise`

> ⚠️ This translation is AI-generated and pending native review. See [中文 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-zh.md) for terminology.

> keiailab operator family 的视觉身份、声音和语调。

本文档是 `forgewise` 品牌决策的 canonical 参考。适用于 README、发布说明、营销资料以及代表项目的所有第三方沟通。

## 1. 身份

**组织**: [keiailab](https://keiailab.com) — Kubernetes-native 数据平台操作器 (MIT-licensed, license-clean, vanilla-upstream 兼容).

**项目**: `forgewise` — MIT-licensed MCP-native 开发者智能 — 开源、本地执行、以确定性分析实现 GitLab Duo Enterprise 类工具表面。

**Family**: 共享 keiailab 治理基线的 5 个 sister 项目之一。`forgewise` 是*唯一的 Python 项目* (其他是基于 Go 的 Kubernetes 操作器):

| 项目 | 语言 | 领域 | 仓库 |
|---|---|---|---|
| `postgres-operator` | Go | Kubernetes 操作器 (PostgreSQL 18+) | https://github.com/keiailab/postgres-operator |
| `mongodb-operator` | Go | Kubernetes 操作器 (MongoDB 7.0+) | https://github.com/keiailab/mongodb-operator |
| `valkey-operator` | Go | Kubernetes 操作器 (Valkey 8.0+) | https://github.com/keiailab/valkey-operator |
| `operator-commons` | Go | 3 操作器共享 Go 库 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | **Python 3.11+** | **MCP-native 开发者智能** | https://github.com/keiailab/forgewise |

## 2. Logo + 视觉资产

| 资产 | URL | 用途 |
|---|---|---|
| Primary logo (SVG) | `https://keiailab.com/assets/logo.svg` | README 头部、幻灯片 |
| Mono mark | `https://keiailab.com/assets/mark.svg` | Favicon、社交卡片 |
| Wordmark | `https://keiailab.com/assets/wordmark.svg` | Footer、dark 背景 |

**Logo 位置**: README 上部居中,宽度 120px。始终链接到 https://keiailab.com。

**Clear space**: Logo 周边最小 padding = logo 宽度的 25%。

**禁止**:
- 修改 logo 颜色
- 添加 drop shadow / filter
- 放置在对比度不足的背景上
- 未经 keiailab 品牌批准与其他 logo 组合

## 3. 色彩调色板

| 角色 | Hex | 用途 |
|---|---|---|
| Primary (keiailab teal) | `#0EA5A8` | 头部、primary 操作、链接 |
| Secondary (deep navy) | `#0F172A` | Dark 背景、代码块 |
| Accent (warm amber) | `#F59E0B` | 高亮、badge 强调 |
| Neutral grey | `#64748B` | Light 背景上的正文文字 |
| Background light | `#F8FAFC` | 文档页面背景 |
| Background dark | `#020617` | 代码编辑器主题、dark mode |

GitHub README 的 shield.io badge 推荐使用上述 hex。

## 4. 排版

- **标题**: 系统默认 (GitHub 的 default `-apple-system, BlinkMacSystemFont, Segoe UI, ...`)
- **正文**: 同上 (GitHub-native 整合)
- **代码**: `ui-monospace, SFMono-Regular, Consolas, ...` (GitHub 的 default monospace)

不使用单独的 webfont (GitHub README rendering 整合)。

## 5. 声音 + 语调

**目标读者**: 平台工程师 / DevOps / SRE / 开发者体验 (DX) 团队 — GitLab 自托管运维或 MCP-native 开发工具评估者。

**声音原则**:
- **Direct** — 尽可能用 bullet point 而非段落
- **Evidence-based** — 主张需附带 benchmark / SLA / 链接
- **Vendor-neutral** — 功能上与 GitLab Duo Enterprise 兼容,但不嵌入 Duo 商标或 proprietary code
- **License-aware** — 仅依赖 MIT/BSD/Apache-2.0/PSF; 拒绝 SaaS 表面的 SSPL / 著佐权
- **Deterministic-first** — MVP 零外部 LLM 调用; 内部 LLM 路由器是 opt-in attach point

**避免**:
- 营销最高级表达 ("blazing fast", "革命性", "最佳")
- 模糊比较 ("X-class 质量") — *用具体指标或 benchmark 量化*
- Roadmap 中基于时间的截止日期 (改用功能 checklist)
- 暗示 GitLab 官方合作或 Duo 商标许可的主张

## 6. README 头部标准

所有 README 的首段使用以下格式 (Wave 3 标准 — forgewise 适配):

```markdown
<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# forgewise

> **MIT-licensed MCP-native developer intelligence — GitLab Duo Enterprise-class tools, locally executable, deterministic**

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <!-- 现有 shield.io badges 保留 + 整合 -->
</p>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.ja.md">日本語</a> |
  <b>中文</b>
</p>
```

## 7. README Footer 标准

所有 README + root-level .md 文件末尾附加以下 footer (Wave 3 标准 — forgewise 含 5 repo 整合):

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
  © 2026 keiailab · <a href="LICENSE">MIT</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
```

## 8. Badge 标准顺序

README 的 shield.io badge 顺序 (左→右,forgewise 适配):

1. License (MIT)
2. Python 版本 (3.11+)
3. MCP protocol 版本 (`2025-03-26` / `2025-06-18`)
4. PyPI 包 (release 后)
5. Container Image (ghcr.io/keiailab/forgewise — 发布后)
6. OpenSSF Scorecard
7. GitHub Discussions

## 9. Discussions / Issues / PR 模板

- **Discussions**: `https://github.com/keiailab/forgewise/discussions` — 功能想法、Q&A
- **Issues**: bug 报告 + 带 use case 的具体功能请求 (安全问题走 `SECURITY.md` 流程)
- **PR 模板**: `.github/PULL_REQUEST_TEMPLATE.md` 标准 (用户场景 + 验证命令引用义务,`CONTRIBUTING.md` PR Checklist 整合)

## 10. 社交 + 外部

- **网站**: https://keiailab.com
- **GitHub Org**: https://github.com/keiailab
- **PyPI** (Python 包): https://pypi.org/project/forgewise/ (发布后)
- **GHCR** (容器): https://github.com/keiailab/forgewise/pkgs/container/forgewise (发布后)

## 11. License + 著作权

- License: [MIT](LICENSE)
- Copyright: © 2026 keiailab contributors
- Third-party 著作权: see [NOTICE](NOTICE) (目前未编写 — Python deps 的 license 信息通过 `pyproject.toml` 的 `[project.dependencies]` 与 `uv.lock` 追踪)

## 12. 商标声明

- "GitLab" 和 "GitLab Duo" 是 GitLab Inc. 的注册商标。forgewise *并非* GitLab 或 GitLab Inc. 的官方产品 / 认证 / 合作伙伴。
- forgewise 仅以开源方式提供 GitLab Duo Enterprise 的*功能兼容表面 (feature-compatible surface)*,不包含 GitLab 的 proprietary code 或模型。
- 所有 GitLab API 调用都通过用户自己的 GitLab 实例 + token 执行。

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
  © 2026 keiailab · <a href="LICENSE">MIT</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
