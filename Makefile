# Code Coach — local quality gate. Run `make check` before calling work done.
PY := .venv/bin/python

.PHONY: check test lint type tsc install-dev

check: lint test tsc
	@echo "── all checks passed ──"

test:
	$(PY) -m unittest discover -s tests

lint:
	$(PY) -m ruff check code_coach tests

type:
	$(PY) -m mypy

tsc:
	cd web && npx tsc --noEmit

install-dev:
	$(PY) -m pip install -e ".[dev]"
