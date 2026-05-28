PYTHON ?= 3.11
UV ?= uv
RUN = $(UV) run --python $(PYTHON) --extra dev

.PHONY: lint typecheck test check smoke-gitlab setup-hooks release publish audit-quality docker-build

lint:
	$(RUN) ruff check .

typecheck:
	$(RUN) mypy forgewise tests

test:
	$(RUN) python -m pytest

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

publish: ## PyPI 게시: wheel + sdist 빌드 후 uv publish. 사용: make publish
	rm -rf dist/
	$(UV) build
	$(UV) publish
	@echo "PyPI publish 완료"

docker-build: ## Docker 이미지 빌드 (기본 빌더, linux/amd64). 사용: make docker-build [TAG=forgewise:latest]
	docker buildx build --builder default -t $${TAG:-forgewise:latest} .

audit-quality: ## 5 repo production-grade 자동 측정 (commons SSOT, ADR-0013).
	@bash ../operator-commons/scripts/audit-production-grade.sh ..
