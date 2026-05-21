PYTHON ?= 3.11
UV ?= uv
RUN = $(UV) run --python $(PYTHON) --extra dev

.PHONY: lint typecheck test coverage check smoke-gitlab setup-hooks release audit-quality

lint:
	$(RUN) ruff check .

typecheck:
	$(RUN) mypy forgewise tests

test:
	$(RUN) python -m pytest

coverage: ## pytest --cov term + xml report. fail_under threshold (pyproject) 위배 시 fail.
	$(RUN) python -m pytest --cov --cov-report=term --cov-report=xml

check: lint typecheck test

smoke-gitlab:
	$(RUN) python -m forgewise.smoke_gitlab

setup-hooks:
	@command -v lefthook >/dev/null 2>&1 || { echo "lefthook 미설치 — brew install lefthook 또는 npm install -g lefthook"; exit 1; }
	lefthook install
	@echo "lefthook hooks 설치 완료. detect-secrets baseline 권장: 'uv run detect-secrets scan > .secrets.baseline'"

release: ## 자동 release pipeline (scripts/release.sh). 사용: make release VERSION=v0.1.0
	@[ -n "$(VERSION)" ] || { echo "Usage: make release VERSION=v0.1.0"; exit 1; }
	bash scripts/release.sh $(VERSION)

audit-quality: ## 5 repo production-grade 자동 측정 (commons SSOT, ADR-0013, sister repo 가용 시).
	@if [ -f ../operator-commons/scripts/audit-production-grade.sh ]; then \
		bash ../operator-commons/scripts/audit-production-grade.sh ..; \
	else \
		echo "audit-quality: ../operator-commons 부재 — graceful skip (keiailab operator family 컨텍스트 한정 target)"; \
	fi
