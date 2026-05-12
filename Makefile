PYTHON ?= 3.11
UV ?= uv
RUN = $(UV) run --python $(PYTHON) --extra dev

.PHONY: lint typecheck test check

lint:
	$(RUN) ruff check .

typecheck:
	$(RUN) mypy forgewise tests

test:
	$(RUN) python -m pytest

check: lint typecheck test
