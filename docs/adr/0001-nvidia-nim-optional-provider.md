# ADR-0001: NVIDIA NIM optional LLM provider (opt-in, audit-bound)

- Date: 2026-05-21
- Status: Accepted
- Authors: @eightynine01
- Refs: Codex adversarial review 2026-05-21 (Critical #3 — quota / model retirement / auth / secret SSOT / trust boundary)

## Context

ForgeWise 의 design.md (`docs/design.md`) 는 다음 3 원칙을 명시한다:

- §"엔터프라이즈 경계": *기본 동작은 오프라인, 결정론적, 외부 LLM 미호출* 이다.
- §"MCP 계약": 런타임 의존성은 Python 표준 라이브러리만 사용. self-hosted / 폐쇄망 / 사내 forge 이식 용이성이 목표.
- §"후속 확장 #1": OpenAI-compatible provider router 와 사내 vLLM / Ollama 연결 — *후속 확장* 명시 (core 범위 아님).

본 ADR 의 트리거 = 사용자 요구 (2026-05-21 다중 repo cleanup 의 NVIDIA NIM optional provider 항목):
> 기능 하나 추가로 nvidia cloud api 무료 발급방법과 선택적으로 api 추가하는것

NVIDIA NIM (`https://integrate.api.nvidia.com/v1`) 는 OpenAI-compatible surface 를 제공한다. 단순 라이브러리 import / 환경변수 등록 만으로 LLM router 가 추가될 수 있다.

그러나 본 통합은 *단순 기능 추가가 아닌 제품 경계 변경* 이다. Codex adversarial review (2026-05-21 RFC-0045 §2.5 stage 3) 의 Critical #3 challenge:

> forgewise NIM 통합은 "자연스러운 추가"가 아니라 제품 경계 변경입니다.
> design.md §59 는 런타임 표준 라이브러리 지향, §91 는 기본 오프라인·결정론적·외부 LLM 미호출, §108 는 OpenAI-compatible router 를 후속 확장으로 둡니다.
> 외부 LLM 호출 기능은 audit / security / product-contract 변경입니다.

본 결정은 *opt-in 제약 의무화* + *audit 의무화* 로 product boundary 를 명시 보존한다.

## Decision

NVIDIA NIM 을 *opt-in 외부 LLM provider* 로 추가한다. 다음 5 제약을 모두 만족하는 경우만 활성:

1. **이중 env 의무**: `LLM_PROVIDER=nvidia` 환경변수 명시 + `NVIDIA_API_KEY` 환경변수 명시. 둘 중 하나라도 부재 시 = `deterministic` 기본값 (외부 LLM 호출 없음).
2. **Tool annotation opt-in**: tool registry 의 각 tool 은 `requires_llm: bool` annotation 보유. `False` (default) tool 은 *NVIDIA provider 활성에도 외부 호출 없음*. `True` (예: `code_explanation_extended`) tool 만 외부 호출.
3. **Audit log 의무**: 모든 외부 LLM 호출 = `forgewise.audit.jsonl` 에 기록. 호출 metadata (model / prompt SHA / response size / latency / API key fingerprint masked) 포함. 기록 실패 시 호출 차단.
4. **Quota guard**: rate-limit-aware backoff + retry. 429 응답 시 exponential backoff (1s → 16s, max 4 retry). 5xx 응답 시 fallback to deterministic + audit 로그 명시.
5. **Default deterministic fallback**: NVIDIA NIM 호출 실패 / quota 소진 / network 차단 시 *deterministic 모드로 graceful degrade*. 사용자 가시 결과 = "LLM provider unavailable, deterministic result returned" notice.

### 구조

```
forgewise/forgewise/
├── llm/                          ← 신규 패키지
│   ├── __init__.py
│   ├── base.py                   ← LLMProvider Protocol + DeterministicProvider (default)
│   ├── nvidia_nim.py             ← NVIDIANIMProvider (httpx, OpenAI-compatible)
│   └── router.py                 ← env-driven provider 선택 + audit + fallback
├── audit.py                      ← (기존) LLM 호출 metadata 통합
└── tools.py                      ← tool registry 에 `requires_llm` annotation 추가
```

### 의존성

- `httpx` (이미 `pyproject.toml` dependencies 포함, 추가 X)
- Python 표준 라이브러리 우선 원칙 보존 (httpx 는 기존 의존성)
- NVIDIA NIM API = OpenAI-compatible surface, custom SDK 추가 X

### Free tier 약관

NVIDIA NIM 의 free tier 약관 (credit 한도 / rate limit) 은 *NVIDIA 측에서 변동* 한다 (Codex adversarial review Critical #2 적시 — 2025 년 forum 답변 기준 credit 모델 변경 발생). 본 ADR 본문 + `docs/nvidia-setup.md` 은 **build.nvidia.com 의 공식 약관을 참조** 라고 명시. 본 ForgeWise 코드는 약관 본문을 *내장하지 않는다* (drift 위험).

## Consequences

### 긍정

- ForgeWise 사용자가 외부 LLM (NVIDIA NIM) 을 *선택적* 으로 활용 가능 → 결과 품질 향상 옵션
- 추가 dependency 0 (httpx 기존)
- opt-in 제약으로 product boundary 명시적 보존
- audit log 의무화 → enterprise 환경 (사내 forge / 폐쇄망) 에서도 외부 호출 추적 가능
- 사용자 요구 11 충족

### 부정

- 외부 LLM 호출 = audit / security 표면 확장
- NVIDIA NIM API 의 약관 변동 시 docs drift risk (caveat 명시로 일부 완화)
- 사용자 환경 설정 복잡도 증가 (`LLM_PROVIDER` + `NVIDIA_API_KEY` 양 env)
- 폐쇄망 환경에서 NVIDIA NIM 활성 = 외부 ingress 의무 (사용자 결정)

### Tradeoff

- design.md §91 "기본 동작 오프라인 / 결정론적 / 외부 LLM 미호출" 원칙 = **default 정합 보존**
- §108 후속 확장 #1 "OpenAI-compatible provider router" = **본 ADR 가 그 후속 확장의 첫 인스턴스**
- 외부 LLM 호출 표면 추가 vs 사용자 요구 11 → opt-in + audit 로 tradeoff 최적화

### 후속 작업

- `forgewise/llm/` 패키지 신규 (TDD)
- `forgewise/tools.py` 에 `requires_llm` annotation 추가
- `forgewise/audit.py` 통합 (LLM call metadata)
- `tests/test_nvidia_nim.py` (httpx mocked + integration test skip)
- `docs/nvidia-setup.md` + 3-언어 (KO/JA/ZH) — build.nvidia.com 회원가입 path + 약관 caveat
- forgewise v0.2.0 tag (NVIDIA NIM provider 안정화 후)

## Alternatives Considered

### A. 별도 repo (`forgewise-nvidia-provider`)

- **거절 이유**: deployment 복잡도 증가 (사용자가 2 repo 관리). dependency 그래프 추가. ForgeWise core 의 stability tier 와 sync 부담.
- **유지된다면**: design.md §"엔터프라이즈 경계" 보존 가장 강력. core repo 무변경.
- 결과: forgewise core 의 `llm/` 패키지 안에 = opt-in 제약 + audit + product boundary 명시로 충분.

### B. tool 단위 monkey-patch (env 만 활성)

- **거절 이유**: tool registry 의 `requires_llm` annotation 표면 없음 → 모든 tool 이 NVIDIA 호출 가능 → audit 표면 불명확. enterprise 환경 진단 어려움.
- 결과: tool annotation 의무로 *어느 tool 이 외부 호출* 명시.

### C. 본 ADR 채택 (선택)

- opt-in env + tool annotation + audit + quota + fallback 5 제약
- design.md 원칙 default 보존 + 후속 확장 #1 의 첫 인스턴스 명시
- product boundary = ADR 본문 + tool annotation + audit log 3 layer 로 enforce

## Refs

- design.md (`docs/design.md`) §"MCP 계약" + §"엔터프라이즈 경계" + §"후속 확장"
- Codex adversarial review 2026-05-21 (RFC-0045 §2.5 stage 3) — Critical #3
- 사용자 요구 2026-05-21 (NVIDIA cloud API 무료 발급 + nim_code_review MCP tool 통합)
- 관련 spec: `docs/nvidia-nim-setup.md` (free-tier signup + API key SSOT + tool usage)
- NVIDIA NIM official endpoint: https://integrate.api.nvidia.com/v1
- NVIDIA NIM API docs: https://docs.api.nvidia.com/nim/reference/llm-apis
- NVIDIA developer forum (credit/rate-limit 변동 evidence): https://forums.developer.nvidia.com/t/request-more-4-000-credits-option-on-build-nvidia-com/344567
- 관련 ADR (참고): operator-commons `docs/kb/adr/0001-keiailab-operator-commons-charter.md` (별도 repo charter pattern), mongodb-operator `docs/kb/adr/0001-controllerutil-createorupdate-pattern.md` (Nygard 5-섹션 pattern)
