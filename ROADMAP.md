# ForgeWise Roadmap

본 문서는 ForgeWise 의 향후 개발 방향 + 우선순위. 일정은 *비확정* — 커뮤니티 요청 +
maintainer 가용성에 따라 조정.

## 🎯 v0.x — 현재 (2026 Q2)

### 완료 (main 머지)
- ✅ MCP server bootstrap (CLI + HTTP + protocol)
- ✅ GitLab REST API 호환 (15 surface)
- ✅ GitLab Duo 호환 surface (18 tool)
- ✅ OAuth 2.0 (read_repository + read_api scope)
- ✅ tools.py 통합 카탈로그 (33 MCP tool)
- ✅ 거버넌스 5종 (SECURITY/CONTRIBUTING/CODE_OF_CONDUCT/CHANGELOG/AGENTS)
- ✅ 운영 4종 docs (installation/configuration/api-reference/upgrade)
- ✅ lefthook Python 4계층 (ruff + mypy strict + pytest + DCO + Conventional)
- ✅ README 4-lang (en canonical + ko/ja/zh placeholder/일부)
- ✅ tests/test_governance.py 38/38 PASS

## 📅 v0.1 — 첫 stable (2026 Q3 예정)

### P0 (반드시)
- [ ] PyPI publish (현재 git install 만)
- [ ] CHANGELOG.md 첫 release entry
- [ ] Docker image (multi-arch opt-in)
- [ ] Helm chart (Kubernetes deployment)
- [ ] E2E 테스트 (실 GitLab CE 인스턴스 연동)

### P1 (가능 시)
- [ ] MCP tool input schema validation 강화
- [ ] OAuth refresh token rotation
- [ ] structured logging (json) + log level env var
- [ ] metrics (Prometheus exposition)

## 🔮 v0.2+ — 후속 (2026 Q4+)

### MCP surface 확장
- [ ] GitLab issues + merge_requests 추가 surface
- [ ] GitLab CI/CD pipeline 트리거 + log streaming
- [ ] GitLab snippets / wiki / packages 호환

### Duo compat 강화
- [ ] Duo Chat 호환 protocol
- [ ] Duo Code Suggestions 컨텍스트 manager

### 운영
- [ ] caching layer (Redis 옵션)
- [ ] rate limit 가시화
- [ ] multi-instance 지원 (GitLab + GitHub + Bitbucket 통합)

### 보안
- [ ] OIDC + SAML SSO 옵션
- [ ] secret scanning hook (lefthook detect-secrets)
- [ ] supply chain SLSA L3 (cosign keyless 서명)

## 🌐 다국어 (S4 sub-cycle)

- [x] README 4-lang 골격
- [ ] docs/ 전체 4-lang (S4-D cycle 진행 중)
- [ ] glossary cross-link (commons SSOT)
- [ ] native reviewer (ja/zh) `[검토 필요]` → `[reviewed]` 승격

## 📊 v3.x-stable 가족 정합

ForgeWise 가 keiailab family 의 *5번째* repo (postgres / mongodb / valkey
operator + operator-commons + forgewise). v3.x-stable 선언은 5 repo *모두*
의 audit 조건 충족 시.

- [ ] 5 repo audit `commons/scripts/audit-production-grade.sh` 모든 ✅
- [ ] forgewise 의 P0/P2/OP audit gap (audit P0-2/4/9, P2-2/8/9, OP-1/5/6)
  현 본 ROADMAP commit 으로 부분 해소
- [ ] commons/docs/specs/2026-05-21-v3x-stable-declaration-design.md (S8)
  의 success criteria 모두 충족

## 🙋 contributing

본 ROADMAP 의 변경 / 추가 / 우선순위 조정은 PR 또는 issue 환영. 본 문서는
*살아있는 문서* — 커뮤니티 요청 + 실 사용 사례 따라 조정.

## 관련

- [README](README.md) — 현재 기능
- [CHANGELOG](CHANGELOG.md) — 머지된 변경
- [AGENTS](AGENTS.md) — Tier-3 프로젝트 컨벤션
- [keiailab family](docs/family.md) — operator 4 + ForgeWise 의 가족 구성
- [v3.x-stable 선언](https://github.com/keiailab/operator-commons/blob/main/docs/specs/2026-05-21-v3x-stable-declaration-design.md) — family 차원의 release 조건
