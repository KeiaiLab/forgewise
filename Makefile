PYTHON ?= 3.11
UV ?= uv
RUN = $(UV) run --python $(PYTHON) --extra dev

.PHONY: lint typecheck test check smoke-gitlab setup-hooks

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
