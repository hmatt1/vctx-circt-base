SHELL := /usr/bin/env bash
PYTHON ?= .venv/bin/python
CIRCT_DIR ?= ./circt
GITHUB_OWNER ?= $(shell git config --get remote.origin.url | sed -E 's#.*github.com[:/]([^/]+)/.*#\1#')
REPO_NAME ?= $(shell basename -s .git $$(git config --get remote.origin.url))
CIRCT_BASE_IMAGE ?= ghcr.io/$(GITHUB_OWNER)/$(REPO_NAME)-circt-base:main

.PHONY: bootstrap-python setup verify-free-threading install-circt lint typecheck test test-integration test-integration-container format run clean

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

test-integration-container:
	docker run --rm \
		-v "$(PWD):/workspace" \
		-w /workspace \
		$(CIRCT_BASE_IMAGE) \
		bash -lc 'python3.14t -m pip install --upgrade pip && python3.14t -m pip install -e .[dev] && bash ./scripts/run_circt_integration.sh python3.14t'

format:
	$(PYTHON) -m ruff check src tests --fix

run:
	$(PYTHON) -m circt_hello.cli

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache build dist *.egg-info
