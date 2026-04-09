SHELL := /usr/bin/env bash
PYTHON ?= .venv/bin/python
CIRCT_DIR ?= ./circt

.PHONY: bootstrap-python setup verify-free-threading install-circt lint typecheck test test-integration format run clean

bootstrap-python:
	./scripts/bootstrap_python314t.sh

setup:
	./scripts/setup_env.sh

verify-free-threading:
	$(PYTHON) -c "import sys; print(sys.version); print('gil_enabled=', sys._is_gil_enabled()); assert not sys._is_gil_enabled()"

install-circt:
	BUILD_CIRCT_FROM_SOURCE=1 ./scripts/install_circt_bindings.sh $(CIRCT_DIR)

lint:
	$(PYTHON) -m ruff check src tests

typecheck:
	$(PYTHON) -m mypy src tests

test:
	$(PYTHON) -m pytest -m "not integration"

test-integration:
	$(PYTHON) -m pytest -m integration

format:
	$(PYTHON) -m ruff check src tests --fix

run:
	$(PYTHON) -m circt_hello.cli

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
