# 브랜딩 가이드 — `forgewise`

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> keiailab operator family 의 시각 정체성, 목소리, 톤.

본 문서는 `forgewise` 브랜딩 결정의 canonical 참조입니다. README, release note, 마케팅 자료, 그리고 프로젝트를 대표하는 모든 외부 커뮤니케이션에 적용됩니다.

## 1. 정체성

**조직**: [keiailab](https://keiailab.com) — Kubernetes-native 데이터 플랫폼 오퍼레이터 (Apache-2.0, license-clean, vanilla-upstream 호환).

**프로젝트**: `forgewise` — Apache-2.0 MCP-native 개발자 인텔리전스 — 오픈소스, 로컬 실행, GitLab Duo Enterprise 류 도구 표면을 결정론적 분석으로 구현.

**Family**: keiailab 거버넌스 기준선을 공유하는 5 sister 프로젝트의 하나. `forgewise` 는 *유일한 Python 프로젝트* (나머지는 Go 기반 Kubernetes 오퍼레이터):

| 프로젝트 | 언어 | 도메인 | 저장소 |
|---|---|---|---|
| `postgres-operator` | Go | Kubernetes 오퍼레이터 (PostgreSQL 18+) | https://github.com/keiailab/postgres-operator |
| `mongodb-operator` | Go | Kubernetes 오퍼레이터 (MongoDB 7.0+) | https://github.com/keiailab/mongodb-operator |
| `valkey-operator` | Go | Kubernetes 오퍼레이터 (Valkey 8.0+) | https://github.com/keiailab/valkey-operator |
| `operator-commons` | Go | 3 오퍼레이터의 공유 Go 라이브러리 | https://github.com/keiailab/operator-commons |
| **`forgewise`** | **Python 3.11+** | **MCP-native 개발자 인텔리전스** | https://github.com/keiailab/forgewise |

## 2. 로고 + 비주얼 자산

| 자산 | URL | 용도 |
|---|---|---|
| Primary 로고 (SVG) | `https://keiailab.com/assets/logo.svg` | README 헤더, 슬라이드 |
| Mono mark | `https://keiailab.com/assets/mark.svg` | Favicon, 소셜 카드 |
| Wordmark | `https://keiailab.com/assets/wordmark.svg` | Footer, dark 배경 |

**로고 배치**: README 상단 중앙, 너비 120px. 항상 https://keiailab.com 으로 링크.

**Clear space**: 로고 주변 최소 padding = 로고 너비의 25%.

**금지**:
- 로고 색상 변경
- Drop shadow / filter 추가
- 대비가 부족한 배경 위 배치
- keiailab 브랜드 승인 없이 다른 로고와 결합

## 3. 색상 팔레트

| 역할 | Hex | 용도 |
|---|---|---|
| Primary (keiailab teal) | `#0EA5A8` | 헤더, primary 액션, 링크 |
| Secondary (deep navy) | `#0F172A` | Dark 배경, 코드 블록 |
| Accent (warm amber) | `#F59E0B` | Highlight, badge accent |
| Neutral grey | `#64748B` | Light 배경 위 본문 텍스트 |
| Background light | `#F8FAFC` | 문서 페이지 배경 |
| Background dark | `#020617` | 코드 에디터 테마, dark mode |

GitHub README 의 shield.io badge 는 위 hex 사용 권장.

## 4. 타이포그래피

- **헤딩**: 시스템 기본 (GitHub 의 default `-apple-system, BlinkMacSystemFont, Segoe UI, ...`)
- **본문**: 동일 (GitHub-native 정합)
- **코드**: `ui-monospace, SFMono-Regular, Consolas, ...` (GitHub 의 default monospace)

별도 webfont 사용 안 함 (GitHub README rendering 정합).

## 5. 목소리 + 톤

**대상 독자**: 플랫폼 엔지니어 / DevOps / SRE / 개발자 경험 (DX) 팀 — GitLab self-hosted 운영자 또는 MCP-native 개발 도구 평가자.

**목소리 원칙**:
- **Direct** — 가능한 한 단락보다 bullet point
- **Evidence-based** — 주장은 benchmark / SLA / 링크를 동반
- **Vendor-neutral** — GitLab Duo Enterprise 와 기능 호환하되, Duo 상표 또는 proprietary code 를 embed 하지 않음
- **License-aware** — Apache-2.0 + MIT/BSD/PSF dependency 만; SaaS 표면에 SSPL / 카피레프트 거부
- **Deterministic-first** — MVP 는 외부 LLM 호출 0; 사내 LLM 라우터는 opt-in attach point

**회피**:
- 마케팅 최상급 표현 ("blazing fast", "혁신적", "최고")
- 모호한 비교 ("X-class 품질") — *구체 메트릭 또는 벤치마크로 정량화*
- Roadmap 의 시간 기반 마감 (대신 기능 체크리스트)
- GitLab 공식 파트너십 또는 Duo 상표 라이선스를 암시하는 주장

## 6. README 헤더 표준

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
  <a href="README.md">English</a> |
  <b>한국어</b> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.zh.md">中文</a>
</p>
```

## 7. README Footer 표준

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

## 8. Badge 표준 순서

README 의 shield.io badge 순서 (좌→우, forgewise 적응):

1. License (Apache-2.0)
2. Python 버전 (3.11+)
3. MCP protocol 버전 (`2025-03-26` / `2025-06-18`)
4. PyPI 패키지 (release 후)
5. Container Image (ghcr.io/keiailab/forgewise — 게시 후)
6. OpenSSF Scorecard
7. GitHub Discussions

## 9. Discussions / Issues / PR 템플릿

- **Discussions**: `https://github.com/keiailab/forgewise/discussions` — 기능 제안, Q&A
- **Issues**: 버그 리포트 + 사용 사례 기반의 구체 기능 요청 (보안 이슈는 `SECURITY.md` 절차)
- **PR 템플릿**: `.github/PULL_REQUEST_TEMPLATE.md` 표준 (사용자 시나리오 + 검증 명령 인용 의무, `CONTRIBUTING.md` PR Checklist 정합)

## 10. 소셜 + 외부

- **웹사이트**: https://keiailab.com
- **GitHub Org**: https://github.com/keiailab
- **PyPI** (Python 패키지): https://pypi.org/project/forgewise/ (게시 후)
- **GHCR** (컨테이너): https://github.com/keiailab/forgewise/pkgs/container/forgewise (게시 후)

## 11. License + 저작권

- License: [Apache-2.0](LICENSE)
- Copyright: © 2026 keiailab contributors
- Third-party 저작권 표기: see [NOTICE](NOTICE) (현재 미작성 — Python deps 의 license 표기는 `pyproject.toml` 의 `[project.dependencies]` 와 `uv.lock` 으로 추적)

## 12. 상표 고지

- "GitLab" 및 "GitLab Duo" 는 GitLab Inc. 의 등록 상표입니다. forgewise 는 GitLab 또는 GitLab Inc. 의 공식 제품 / 인증 / 파트너 관계가 *아닙니다*.
- forgewise 는 GitLab Duo Enterprise 의 *기능 호환 표면 (feature-compatible surface)* 만 오픈소스로 제공하며, GitLab 의 proprietary code 또는 모델을 포함하지 않습니다.
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
