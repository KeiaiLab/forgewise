# AGENTS.md — ForgeWise (Tier-3 프로젝트 override) [한국어]

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> [English](AGENTS.md) | **한국어** | [日本語](AGENTS.ja.md) | [中文](AGENTS.zh.md)

> 본 문서는 글로벌 거버넌스 (Tier-1 `~/.claude/CLAUDE.md` + Tier-2 `~/.claude/standards/*.md`)
> 에 대한 ForgeWise 프로젝트 특이성 (Python 전용 스택) override 를 기술합니다.
> RFC-0001 (글로벌 부트스트랩) 정합. 본 문서가 글로벌과 충돌할 경우 우선순위 §3 에
> 따라 **사용자 명시 지시 > Tier-3 (본 문서) > Tier-2 standards > Tier-1 글로벌**.

> **NOTE**: AGENTS.md canonical 은 한국어로 작성되어 있어 본 .ko.md 는 사실상 1:1
> 사본이지만, language banner + warning 배너 + glossary cross-link 일관성을 위해
> 별 파일로 유지합니다. 실제 source-of-truth 는 [AGENTS.md](AGENTS.md) 입니다.

## 0. import 계층

```
@~/.claude/CLAUDE.md                      # Tier-1 (글로벌 원칙 + 메타규약)
@~/.claude/standards/principles.md        # Tier-2 (운영 원칙)
@~/.claude/standards/linting.md           # Tier-2 (린팅 — Go 전제, 본 문서에서 Python override)
@~/.claude/standards/testing.md           # Tier-2 (테스트 — Go 전제, 본 문서에서 Python override)
@~/.claude/standards/ci.md                # Tier-2 (로컬 4 계층)
@~/.claude/standards/adr.md               # Tier-2 (ADR 양식)
@~/.claude/standards/enforcement.md       # Tier-2 (강제·자가수정)
@./docs/specs/2026-05-21-forgewise-governance-and-ops-alignment-design.md  # S6 spec
```

## 1. ForgeWise 의 고유성 (Why a Tier-3 override exists)

ForgeWise 는 `keiailab` operator family 의 *유일한 Python 프로젝트* 입니다. 자매 프로젝트:

| Repo | 언어 | 도메인 |
|---|---|---|
| `valkey-operator` | Go | Kubernetes operator (Valkey/Redis) |
| `postgres-operator` | Go | Kubernetes operator (PostgreSQL) |
| `mongodb-operator` | Go | Kubernetes operator (MongoDB) |
| `operator-commons` | Go | Kubernetes operator 공통 라이브러리 |
| **`forgewise`** | **Python 3.11+** | **MCP-native developer intelligence** |

따라서 글로벌 standards 의 Go 전제 gate (gofmt / go vet / golangci-lint / govulncheck) 가
직접 적용되지 않습니다. 동일 *정합성 정신* 을 Python 스택으로 *번역* 합니다. 일탈 사유는
ADR `docs/kb/adr/0001-python-stack-override-vs-global-go-standards.md` 에 정당화됩니다.

상세 내용은 [AGENTS.md](AGENTS.md) 의 §2-§7 참조 (canonical).

## 8. 더 보기

- [AGENTS.md](AGENTS.md) — canonical (한국어 source-of-truth)
- [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md)
- [Korean Contributor Guide (CONTRIBUTING.ko.md)](CONTRIBUTING.ko.md)
- [Security Policy (SECURITY.ko.md)](SECURITY.ko.md)

---

Signed-off-by: TaeHwan Park <eightynine01@gmail.com>
