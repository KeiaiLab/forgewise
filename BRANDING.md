# Branding Guide — `forgewise`

> Visual identity, voice, and tone for the keiailab operator family.

This document is the canonical reference for `forgewise` branding decisions. It applies to the README, release notes, marketing material, and any third-party communication that represents the project.

## 1. Identity

**Organization**: [keiailab](https://keiailab.com) — Kubernetes-native data platform operators + developer intelligence tooling (Apache-2.0, license-clean).

**Project**: `forgewise` — Open-source MCP-native developer intelligence for code forges — GitLab / GitHub / Gitea / Forgejo. Provides GitLab Duo Enterprise-class assistant features as a locally executable, MCP-native tool surface (CLI `forgewise`, stdio MCP `forgewise-mcp`, HTTP MCP `forgewise-http`).

**Family**: One of five sister projects in the keiailab open-source portfolio:

| Project | Tier | Stack | Repository |
|---|---|---|---|
| `operator-commons` | Library | Go | https://github.com/keiailab/operator-commons |
| `postgres-operator` | Operator | Go (K8s) | https://github.com/keiailab/postgres-operator |
| `mongodb-operator` | Operator | Go (K8s) | https://github.com/keiailab/mongodb-operator |
| `valkey-operator` | Operator | Go (K8s) | https://github.com/keiailab/valkey-operator |
| `forgewise` | MCP server | Python | https://github.com/keiailab/forgewise |

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

**Audience**: Platform engineers / DevOps / SRE / developers using MCP-native tooling against GitLab / GitHub / Gitea / Forgejo.

**Voice principles**:
- **Direct** — bullet-point over paragraph where possible
- **Evidence-based** — claims include benchmark / SLA / link
- **Vendor-neutral** — supports all code forges (GitLab, GitHub, Gitea, Forgejo); does not favor one
- **Trademark-aware** — never reference "GitLab Duo" as the product name; describe ForgeWise as an open-source feature-compatible surface
- **License-aware** — Apache-2.0 only, no AGPL/BUSL/SSPL dependencies

**Avoid**:
- Marketing superlatives ("blazing fast", "revolutionary", "best-in-class")
- Direct GitLab Duo product comparisons ("GitLab Duo Pro replacement") — describe capability surface instead
- Vague comparisons ("Enterprise-class quality") — *qualify with specific feature group or audit log evidence*
- Time-based deadlines in roadmap (use `standards/roadmap.md §1.1` — feature checklist instead)

## 6. GitLab Duo Trademark Policy

`forgewise` deliberately avoids the "GitLab Duo" trademark in direct product positioning. The README, marketing material, and external communication use the following framing:

- ✅ "Open-source MCP-native developer intelligence" — neutral positioning
- ✅ "Provides feature surface comparable to GitLab Duo Enterprise" — capability-level reference, not branding equivalence
- ✅ "GitLab Duo Enterprise-class features" — adjectival use only in technical comparison context
- ❌ "GitLab Duo alternative" / "GitLab Duo replacement" — implies trademark substitution
- ❌ "ForgeWise Duo" / "Open-source Duo" — creates trademark confusion

When in doubt, describe the *capability* (code explanation, review, security explanation, RCA, test gen, change summary) rather than the *competitor brand*.

## 7. README Header Standard

모든 README 의 첫 문단은 다음 형식 (Wave 3 표준):

```markdown
<p align="center">
  <img src="https://keiailab.com/assets/logo.svg" alt="keiailab" width="120"/>
</p>

# forgewise

> **Open-source MCP-native developer intelligence for code forges — GitLab / GitHub / Gitea / Forgejo**

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

## 8. README Footer Standard

모든 README + root-level .md 파일의 마지막에 다음 footer 부착 (Wave 3 표준):

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

<p align="center">© 2026 keiailab · Apache-2.0 · <a href="https://keiailab.com">keiailab.com</a></p>
```

## 9. Badges 표준 순서

README 의 shield.io badge 순서 (좌→우):

1. License (Apache-2.0)
2. Python Version (3.11+)
3. PyPI Package (`forgewise` on pypi.org once published)
4. MCP Compatibility (model context protocol logo / version)
5. OpenSSF Scorecard
6. GitHub Discussions

> **Note**: `forgewise` 는 *Python MCP server* 라 Kubernetes / Container Image / Helm Chart badge 는 사용 안 함. 본 도구는 PyPI + uvx + MCP stdio/HTTP 중심.

## 10. Discussions / Issues / PR Templates

- **Discussions**: `https://github.com/keiailab/forgewise/discussions` — feature group requests, MCP client integration, tool surface 제안
- **Issues**: bug reports + concrete feature requests with use case (target code forge 명시 권장 — GitLab / GitHub / Gitea / Forgejo)
- **PR template**: `.github/PULL_REQUEST_TEMPLATE.md` 표준 (사용자 시나리오 + 검증 명령 인용 의무, `standards/checklist.md §3`)

## 11. Social & External

- **Website**: https://keiailab.com
- **GitHub Org**: https://github.com/keiailab
- **PyPI**: (pending publish)
- **MCP Registry**: (pending submission to modelcontextprotocol.io community registry)

## 12. License & Attribution

- License: [Apache-2.0](LICENSE)
- Copyright: © 2026 keiailab contributors
- Third-party attributions: see `docs/references.md`

---

<p align="center">
  <b>keiailab operator family</b><br/>
  <a href="https://github.com/keiailab/operator-commons">operator-commons</a> ·
  <a href="https://github.com/keiailab/postgres-operator">postgres-operator</a> ·
  <a href="https://github.com/keiailab/mongodb-operator">mongodb-operator</a> ·
  <a href="https://github.com/keiailab/valkey-operator">valkey-operator</a> ·
  <a href="https://github.com/keiailab/forgewise">forgewise</a>
</p>

<p align="center">© 2026 keiailab · <a href="LICENSE">Apache-2.0</a> · <a href="https://keiailab.com">keiailab.com</a></p>
