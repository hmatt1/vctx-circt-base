SHELL := /usr/bin/env bash
PYTHON ?= .venv/bin/python

.PHONY: bootstrap-python setup lint typecheck test test-integration format run clean

bootstrap-python:
	./scripts/bootstrap_python314t.sh

setup:
	./scripts/setup_env.sh

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
