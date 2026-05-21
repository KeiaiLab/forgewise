## Summary
<!-- 변경 요약 (1-3 bullet, "왜" 중심) -->

-
-

## Type of Change
<!-- 해당 항목 [x] -->

- [ ] 🐛 Bug fix (non-breaking)
- [ ] ✨ New feature (non-breaking)
- [ ] 💥 Breaking change (사용자/API 호환 깨짐)
- [ ] 📝 Documentation only
- [ ] ♻️ Refactor (외부 동작 동일)
- [ ] 🔧 Tooling / CI / build
- [ ] 🌐 i18n (다국어 추가/갱신)
- [ ] 🚀 Performance
- [ ] 🛡️ Security

## Test Plan
<!-- 검증 방법 + 결과 인용 (CLAUDE.md §2: "검증되지 않은 성공은 성공이 아니다") -->

- [ ] `make check` 통과 (ruff + mypy --strict + pytest)
- [ ] `lefthook run pre-push` 통과
- [ ] (해당 시) 신규 test 추가 — 커버리지 ≥ 기존
- [ ] (해당 시) `bash scripts/smoke_gitlab.py` 통과
- [ ] (해당 시) MCP tool input schema 검증

## Checklist
<!-- 필수 항목 [x] -->

- [ ] commit message Conventional Commits (`feat: / fix: / docs: / ...`)
- [ ] DCO Signed-off-by trailer (`git commit -s`)
- [ ] 한국어 PR 본문 (CLAUDE.md §2)
- [ ] (breaking 시) `CHANGELOG.md` `[Unreleased]` 의 `### Changed` 또는 `### Removed` 갱신
- [ ] (breaking 시) `docs/upgrade.md` 갱신
- [ ] (security 시) `SECURITY.md` 의 보고 채널 검토
- [ ] (i18n 시) `docs/i18n/` 의 glossary 사용 + ⚠️ AI 번역 warning 배너

## Related
<!-- 관련 issue / PR / spec / ADR -->

- Issue: #
- Spec: `docs/specs/...`
- ADR: `docs/decisions/...` 또는 `docs/kb/adr/...`

## Screenshots / Logs
<!-- (해당 시) -->

```
<test output, error logs, etc.>
```

---

🤖 Generated with [Claude Code](https://claude.com/claude-code) (Opus 4.7, 1M context)
