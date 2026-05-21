# Branding Guide — `forgewise`

> Visual identity, voice, and tone for the keiailab operator family.

This document is the canonical reference for `forgewise` branding decisions. It applies to the README, release notes, marketing material, and any third-party communication that represents the project.

## 1. Identity

**Organization**: [keiailab](https://keiailab.com) — Kubernetes-native data platform operators (Apache-2.0, license-clean, vanilla-upstream compatible).

**Project**: `forgewise` — Apache-2.0 MCP-native developer intelligence — open-source, locally-executable, GitLab Duo Enterprise-class tool surface with deterministic analysis.

**Family**: One of five sister projects sharing the keiailab governance baseline. `forgewise` is the *only Python project* (the others are Go-based Kubernetes operators):

| Project | Language | Domain | Repository |
|---|---|---|---|
| `postgres-operator` | Go | Kubernetes operator (PostgreSQL 18+) | https://github.com/keiailab/postgres-operator |
| `mongodb-operator` | Go | Kubernetes operator (MongoDB 7.0+) | https://github.com/keiailab/mongodb-operator |
| `valkey-operator` | Go | Kubernetes operator (Valkey 8.0+) | https://github.com/keiailab/valkey-operator |
| `operator-commons` | Go | Shared Go library for the 3 operators | https://github.com/keiailab/operator-commons |
| **`forgewise`** | **Python 3.11+** | **MCP-native developer intelligence** | https://github.com/keiailab/forgewise |

## 2. Logo & Visual Assets

| Asset | URL | Usage |
|---|---|---|
| Primary logo (SVG) | `https://keiailab.com/assets/logo.svg` | README header, slides |
| Mono mark | `https://keiailab.com/assets/mark.svg` | Favicon, social cards |
| Wordmark | `https://keiailab.com/assets/wordmark.svg` | Footer, dark backgrounds |

**Logo placement**: Top-center of README, width 120px. Always link to https://keiailab.com.

**Clear space**: Minimum padding around logo = 25% of logo width.

**Do not**:
- Recolor the logo
- Add drop shadows or filters
- Place on backgrounds with insufficient contrast
- Combine with other logos without keiailab brand approval

## 3. Color Palette

| Role | Hex | Usage |
|---|---|---|
| Primary (keiailab teal) | `#0EA5A8` | Headers, primary actions, links |
| Secondary (deep navy) | `#0F172A` | Dark backgrounds, code blocks |
| Accent (warm amber) | `#F59E0B` | Highlights, badge accents |
| Neutral grey | `#64748B` | Body text on light backgrounds |
| Background light | `#F8FAFC` | Documentation page background |
| Background dark | `#020617` | Code editor theme, dark mode |

GitHub README 의 shield.io badge 는 위 hex 사용 권장.

## 4. Typography

- **Headings**: System default (GitHub 의 default `-apple-system, BlinkMacSystemFont, Segoe UI, ...`)
- **Body**: 동일 (GitHub-native 정합)
- **Code**: `ui-monospace, SFMono-Regular, Consolas, ...` (GitHub 의 default monospace)

별도 webfont 사용 안 함 (GitHub README rendering 정합).

## 5. Voice & Tone

**Audience**: Platform engineers / DevOps / SRE / developer experience teams running GitLab self-hosted or evaluating MCP-native developer tooling.

**Voice principles**:
- **Direct** — bullet-point over paragraph where possible
- **Evidence-based** — claims include benchmark / SLA / link
- **Vendor-neutral** — feature-compatible with GitLab Duo Enterprise but never embeds Duo trademark or proprietary code
- **License-aware** — Apache-2.0 + MIT/BSD/PSF dependencies only; reject SSPL and copyleft on the SaaS surface
- **Deterministic-first** — MVP makes zero external LLM calls; in-house LLM router is an opt-in attach point

**Avoid**:
- Marketing superlatives ("blazing fast", "revolutionary", "best-in-class")
- Vague comparisons ("X-class quality") — *qualify with specific metric or benchmark*
- Time-based deadlines in roadmap (use feature checklist instead)
- Claims that imply official GitLab partnership or Duo trademark license

## 6. README Header Standard

모든 README 의 첫 문단은 다음 형식 (Wave 3 표준 — forgewise 적응):

```markdown
<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# forgewise

> **Apache-2.0 MCP-native developer intelligence — GitLab Duo Enterprise-class tools, locally executable, deterministic**

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"/></a>
  <!-- 기존 shield.io badges 유지 + 정합 -->
</p>

<p align="center">
  <b>English</b> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a>
</p>
```

## 7. README Footer Standard

모든 README + root-level .md 파일의 마지막에 다음 footer 부착 (Wave 3 표준 — forgewise 포함 5 repo 정합):

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
  © 2026 keiailab · <a href="LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
```

## 8. Badges 표준 순서

README 의 shield.io badge 순서 (좌→우, forgewise 적응):

1. License (Apache-2.0)
2. Python Version (3.11+)
3. MCP protocol version (`2025-03-26` / `2025-06-18`)
4. PyPI package (when released)
5. Container Image (ghcr.io/keiailab/forgewise — when published)
6. OpenSSF Scorecard
7. GitHub Discussions

## 9. Discussions / Issues / PR Templates

- **Discussions**: `https://github.com/keiailab/forgewise/discussions` — feature ideas, Q&A
- **Issues**: bug reports + concrete feature requests with use case (security issues via `SECURITY.md`)
- **PR template**: `.github/PULL_REQUEST_TEMPLATE.md` 표준 (사용자 시나리오 + 검증 명령 인용 의무, `CONTRIBUTING.md` PR Checklist 정합)

## 10. Social & External

- **Website**: https://keiailab.com
- **GitHub Org**: https://github.com/keiailab
- **PyPI** (Python package): https://pypi.org/project/forgewise/ (게시 후)
- **GHCR** (Container): https://github.com/keiailab/forgewise/pkgs/container/forgewise (게시 후)

## 11. License & Attribution

- License: [Apache-2.0](LICENSE)
- Copyright: © 2026 keiailab contributors
- Third-party attributions: see [NOTICE](NOTICE) (현재 미작성 — Python deps 의 license 표기는 `pyproject.toml` 의 `[project.dependencies]` 와 `uv.lock` 으로 추적)

## 12. Trademark Notice

- "GitLab" 및 "GitLab Duo" 는 GitLab Inc. 의 등록 상표입니다. forgewise 는 GitLab 또는 GitLab Inc. 의 공식 제품 / 인증 / 파트너 관계가 아닙니다.
- forgewise 는 GitLab Duo Enterprise 의 *기능 호환 표면 (feature-compatible surface)* 만을 오픈소스로 제공하며, GitLab 의 proprietary code 또는 모델을 포함하지 않습니다.
- 모든 GitLab API 호출은 사용자의 자체 GitLab 인스턴스 + token 으로 수행됩니다.

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
  © 2026 keiailab · <a href="LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a>
</p>
