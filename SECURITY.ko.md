# 보안 정책 (Security Policy)

> ⚠️ This translation is AI-generated and pending native review. See [한국어 glossary](https://github.com/keiailab/operator-commons/blob/main/docs/i18n/glossary-ko.md) for terminology.

> [English](SECURITY.md) | **한국어** | [日本語](SECURITY.ja.md) | [中文](SECURITY.zh.md)

ForgeWise 는 source code, audit log, GitLab token, OAuth credential 을 처리할
수 있는 `keiailab` 오픈소스 MCP-native 개발자 인텔리전스 도구입니다. 보안을
중요하게 다루며 책임 있는 공개 (responsible disclosure) 에 감사드립니다.

## 지원 버전

alpha 단계 동안에는 `0.x` 시리즈의 latest minor release 만 보안 패치를 받습니다.
`1.0.0` 출시 이후에는 더 긴 LTS window 를 채택합니다 (자세한 내용은 `docs/upgrade.md`).

| 버전 | 지원 여부 |
| ------- | ------------------ |
| `0.1.x` | Yes (current)      |
| `< 0.1` | No                 |

## 취약점 신고

**보안 이슈는 절대 public GitHub issue 로 신고하지 마세요.**

다음 채널 중 하나로 **security@keiailab.org** 에 신고:

1. **권장 — GitHub Security Advisory**
   <https://github.com/keiailab/forgewise/security/advisories/new> 에서
   private advisory 를 작성하세요. 수정 사항이 공개되기 전까지 신고가
   비공개 상태로 유지됩니다.
2. **이메일** — `security@keiailab.org`. PGP key 는 조직 웹사이트에 게시됩니다.

다음을 포함해 주세요:

- ForgeWise version (`forgewise --version` 출력)
- 환경 (OS, Python version, transport — stdio / HTTP)
- 재현 절차 또는 proof-of-concept
- 영향 평가 (data 노출, RCE, auth bypass 등)

## 응답 SLO

| 단계                                | 목표                |
| ----------------------------------- | --------------------- |
| 접수 확인                            | 3 영업일       |
| 초기 트리아지 + severity 평가      | 7 영업일       |
| 패치 또는 문서화된 완화 조치        | 트리아지로부터 30 일   |
| 공개 advisory + CHANGELOG 항목      | 패치 release 시점        |

Severity 는 CVSS 3.1 을 따릅니다. Critical (CVSS >= 9.0) 이슈는 out-of-band
release 를 받을 수 있습니다.

## 알려진 보안 경계

전체 운영 기준선은 `docs/security.md` 참조. 요약:

- **Mutation gate** — 원격 상태를 변경하는 tool (`create_issue`,
  `create_merge_request`, `manage_pipeline`, `create_workitem_note`) 은
  `FORGEWISE_ENABLE_MUTATIONS=1` 이 아닌 한 차단됩니다.
- **OAuth scope** — HTTP transport 는 PKCE (`plain` / `S256`) 가 포함된 OAuth 2.0
  Dynamic Client Registration 을 지원합니다. Redirect URI 는 `https://`,
  `127.0.0.1`, `localhost` 로 제한됩니다.
- **Audit log 마스킹** — `.forgewise/audit.jsonl` 은 키가 `token`, `secret`,
  `password`, `key` 와 일치하는 argument 의 값을 `[REDACTED]` 로 redact 합니다.
- **Prompt-to-artifact 정책** — Tool 출력은 결정론적입니다. MVP 는 외부 LLM
  호출을 하지 않습니다. 사내 LLM router 를 attach 한다면 `docs/security.md` 를
  참조하세요.

## CVE 처리

- 확인된 CVE 는 프로젝트의 GitHub Security 탭에서 추적됩니다.
- `CHANGELOG.md` 에 advisory ID 와 CVE 식별자를 참조하는 `Security` 섹션을
  추가합니다.
- 다운스트림 소비자는 본 저장소의 GitHub Security Advisory feed 를 구독해야
  합니다.

## Token 또는 secret 누출이 의심되는 경우

1. 해당 GitLab token (또는 기타 credential) 을 원본 시스템에서 즉시 폐기.
2. `.forgewise/audit.jsonl` 검사 — redaction layer 가 값을 마스킹해야 합니다.
   마스킹되지 않은 값이 보이면 P0 취약점으로 신고하세요.
3. 위 채널을 통해 Security Advisory 를 제출.

---

*본 정책은 프로젝트 나머지 부분과 함께 MIT 라이선스 하에 배포됩니다.*
