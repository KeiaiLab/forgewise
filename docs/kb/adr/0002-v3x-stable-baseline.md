# ADR 0002: v3.x-stable baseline 인정 (audit ❌ 0 충족)

| 메타 | 값 |
|---|---|
| Status | **Accepted** |
| Date | 2026-05-21 |
| Authors | TaeHwan Park <eightynine01@gmail.com> |
| Supersedes | (없음) |
| Superseded by | (없음) |
| Related | commons-ADR/0013 (audit SSOT), CLAUDE.md §7 (v3.x-stable 정의), forgewise-ADR/0001 (Python 스택 override) |

## Context

CLAUDE.md §7: "본 규약은 **상용 제품 수준**의 다중 프로젝트 일관성을 목표로 한다 — `standards/enforcement.md`의 P0+P1+P2 자동화 모두 충족 시 *v3.x-stable* 선언."

본 repo (forgewise) 는 keiailab family 의 5번째 sister project 로, 3 operator (postgres / mongodb / valkey) + 1 commons 와 별개의 *Python 스택 + MCP server* 특성을 갖는다 (forgewise-ADR/0001 의 Go 전제 standards override 정합). 그럼에도 다음 두 축으로 *v3.x-stable* 진입 조건을 충족했다.

### 1. audit ❌ 0 측정 — 2026-05-21 15:30

`commons/scripts/audit-production-grade.sh` (commons-ADR/0013 SSOT) 가 5 repo (postgres / mongodb / valkey / commons / forgewise) 의 P0 (기본 안전) + P1 (품질 게이트) + P2 (거버넌스) + OP (운영) + C (커뮤니티) 50+ 항목을 자동 측정. 본 repo 의 결과 (Python 도구 매핑 적용):

- P0 (기본 안전): ✅ pre-commit / pre-push / secrets / 한국어 검사 (lefthook + gitleaks)
- P1 (품질 게이트): ✅ ruff (lint+format) / pyright (typecheck) / pytest / build (wheel) / audit
- P2 (거버넌스): ✅ ADR coverage (0001 Python override + 0002 본 baseline) / RFC-0002 GHA 정합 / standards/* 정합 (Go → Python 매핑은 ADR-0001 정합)
- OP (운영): ✅ release.sh / pyproject.toml wheel + sdist publish / stdio MCP server entry point (`forgewise-mcp`) / CLI (`forgewise`)
- C (커뮤니티): ✅ ADOPTERS.md / CONTRIBUTING / CODE_OF_CONDUCT / SECURITY / GOVERNANCE / BRANDING (i18n 4-lang) 정합

audit 시계열 기록: [`commons/docs/quality/audit-history.md`](https://github.com/keiailab/operator-commons/blob/main/docs/quality/audit-history.md) → "🎉 2026-05-21 15:30 — audit ❌ 0 달성" 섹션.

### 2. 거버넌스 baseline

- **RFC-0002 정합** (GitHub Actions 영구 금지) — 본 repo 는 lefthook pre-commit hook 으로 정합. 예외 3종 (Pages 정적 배포 + Dependabot/Renovate + release tag → Release body) 만 허용.
- **i18n 4-lang** (en/ko/ja/zh) README + AGENTS + GOVERNANCE + CONTRIBUTING + CODE_OF_CONDUCT + SECURITY + BRANDING + ADOPTERS + CHANGELOG — supercycle 2026-05-21 Wave 4 완료.
- **Python 스택 override** (forgewise-ADR/0001) — Go 전제 글로벌 standards 의 Python 매핑 (ruff/pyright/pytest) ADR 로 정당화 후 일탈 정합.
- **GitLab Duo Enterprise 호환** — GitLab Duo Pro/Enterprise license 우회 + 동등 기능 surface (workitem note + MR + pipeline + 검색 + label 16 tool) 제공.
- **MCP 네이티브** — stdio MCP server (`forgewise-mcp`) 가 Anthropic Claude Agent SDK / Claude Code 네이티브 통합.

## Decision

본 repo (`keiailab/forgewise`) 를 **v3.x-stable** 로 인정한다.

- *외부 사용자 대상 운영 등급* 으로 공개 가능 — GitLab Duo Pro license 우회가 필요한 self-hosted GitLab 사용자 대상.
- 후속 release tag `vX.Y.Z` 권장 (현 unreleased → v0.1.0 첫 stable release) — 구체 버전은 별 사용자 결정 + 별 ADR 로 추적 (CHANGELOG 정합 + semver 판단).
- 본 ADR 자체는 *baseline 인정* 만 — 실 tag 행위는 사용자가 별도 명시.

## Consequences

### Positive

- **외부 신뢰** — audit 자동 측정 (commons-ADR/0013) + 본 baseline ADR + 거버넌스 4종 + i18n 4-lang + GitLab Duo 호환 매트릭스의 5 축이 *상용 등급* 신뢰 신호로 작용.
- **거버넌스 정합** — Python 스택 override 가 있음에도 audit ❌ 0 달성 → 글로벌 standards 의 *언어 중립성* 입증. 후속 sister project 의 reference.
- **MCP 생태계 진입** — Anthropic Claude Code / Codex 의 native MCP server 패턴 채택 → AI agent 생태계 진입점.
- **GitLab self-hosted 대안** — Duo Pro/Enterprise license 우회로 외부 사용자 (자체 호스팅 GitLab + Claude 결합) 진입 장벽 해소.

### Negative / 회귀 차단 조건

- **audit ❌ ≥ 1 회귀 시** — v3.x-stable 인정 *유지 불가*. 본 ADR 갱신 + commons audit-history 시계열 기록 필수.
- **standards/* 일탈 시** — ADR 부재면 §5 실패. Python 스택 일탈은 ADR-0001 로 정당화 + 후속 일탈도 별 ADR 강제.
- **i18n drift** — 4-lang README / 거버넌스 문서 sync 강제 (readme-i18n-sync hook).
- **MCP API drift** — Anthropic MCP spec 변경 시 stdio interface 회귀 차단. 별 e2e 테스트 보강 필요.

### Trade-offs

- *v3.x-stable 본 선언* (본 ADR) vs *RFC-0005 글로벌 선언 대기* — 본 repo 는 baseline 만 인정하고 글로벌 RFC-0005 는 별 사용자 결정 영역으로 분리. 글로벌 선언 부재 시에도 본 repo 의 audit ❌ 0 자체가 *측정 가능한 운영 등급 신호*.
- *현 unreleased 인정* vs *v0.1.0 첫 stable* — 본 ADR 은 격상 강제 안 함. CHANGELOG 정합 + 사용자 결정.
- *5 sister project 동급 인정* vs *Python 비주류 hold* — 본 ADR 은 동급 인정. Python 스택 특이점은 ADR-0001 + 본 ADR Consequences 의 회귀 차단 조건으로 명시.

## 후속 (v3.1+)

본 baseline 후 v3.1+ 진화 후보:
- P3 성능 게이트 (MCP tool latency budget + throughput benchmark) — 별 ADR
- P4 DR 게이트 (GitLab API rate-limit handling + credential rotation) — 별 ADR
- P5 커뮤니티 KPI (이슈 응답 SLA + adopter 성장 + Anthropic MCP catalog 등록) — 별 ADR
- audit 자동 측정 cron (월 1회) + audit-history 자동 갱신 — commons 측 별 ADR

## 참조

- commons-ADR/0013: `audit-production-grade.sh` 5 repo SSOT 측정 자동화
- commons audit-history (시계열): https://github.com/keiailab/operator-commons/blob/main/docs/quality/audit-history.md
- CLAUDE.md §7 (v3.x-stable 정의): https://github.com/keiailab/.codex (글로벌 standards, private)
- forgewise-ADR/0001: Python 스택 override vs 글로벌 Go 전제 standards
- BRANDING.md (ForgeWise 명명 + GitLab Duo 호환 surface 설명): ../../BRANDING.md
