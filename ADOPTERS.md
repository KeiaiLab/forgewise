# ForgeWise Adopters

본 문서는 ForgeWise 를 production 또는 일상 워크플로에서 사용하는 기관/팀 목록.

## 🏢 Production Adopters

| 조직 | 사용 사례 | 규모 | 시작 시점 | 연락처 |
|---|---|---|---|---|
| _(첫 adopter 환영합니다)_ | — | — | — | — |

## 🧪 Evaluation / PoC

| 조직 | 평가 영역 | 비고 |
|---|---|---|
| keiailab | self-host GitLab MCP + Duo compat 검증 | reference deployment |

## 본인의 사용 사례를 추가하려면

1. PR 으로 본 표에 행 추가 (또는 issue 로 알림)
2. *production* 사용 = 실 환경에서 정기 사용 (PoC 는 별 표)
3. private 도 가능 — 익명/연락처 비공개 OK
4. 사용 사례 1-2 sentence 면 충분

## ForgeWise 의 적합 사례

- **self-host GitLab 사용자** — GitLab Duo Pro/Enterprise 라이선스 없이 Duo MCP surface 호환
- **AI 코딩 도구와 GitLab 연동** — MCP protocol 으로 Claude / Cursor / Cline 등과 연결
- **OAuth 기반 보안 자동화** — repo + api scope 으로 안전한 read-mostly 워크플로
- **MCP server 학습 사례** — Python + ASGI uvicorn + json-schema strict 양식 reference

## 관련

- [README](README.md) — 기능 + Quick Start
- [Use Cases (docs/design.md)](docs/design.md) — 아키텍처 + MCP 계약
- [GitLab Duo compat](docs/references.md) — Duo surface 매핑
- [keiailab family](docs/family.md) — operator 4 + ForgeWise 의 가족 구성
