# CIRCT Hello (Python 3.14t)

A practical, minimal, robust starter project that generates a tiny CIRCT module from Python using the official CIRCT bindings pattern.

## Core policy

- **Always run free-threaded Python (`3.14t`) with GIL disabled.**
- **Build CIRCT from source only once** when creating the base image; do not repeatedly compile CIRCT in normal local/CI workflows.

## What this gives you

- Python package + CLI (`circt-hello`) that prints MLIR.
- Python `3.14t` (free-threaded CPython) bootstrap scripts.
- A strict free-threading verification target (`make verify-free-threading`).
- Tests that run without CIRCT installed, plus integration tests when CIRCT is present.
- GitHub Actions CI (lint, typecheck, unit test on `3.14t`, with runtime free-threading assertion).
- GitHub Codespaces devcontainer pinned to `3.14t`.
- Reusable Docker base image with CIRCT preinstalled.

## Quick start (local)

### 1) Bootstrap Python 3.14t + venv

```bash
make setup
```

Activate env and verify free-threading:

```bash
source .venv/bin/activate
make verify-free-threading
```

Expected: `gil_enabled= False`.

### 2) Run hello world (without requiring local CIRCT build)

```bash
make run
```

If CIRCT bindings are absent, you get a clear guidance error. Standard workflows should use the base image below.

## Build CIRCT once (base image)

```bash
./scripts/build_base_image.sh
```

This is the **intended single place** where the full CIRCT source build happens.

Image includes:
- Ubuntu 24.04 build toolchain,
- Python `3.14t` with `PYTHON_GIL=0`,
- full CIRCT checkout + submodules,
- CIRCT Python bindings preinstalled and import-tested.

## Optional: explicit local CIRCT source build

Only for exceptional cases. Disabled by default to prevent accidental long builds.

```bash
./scripts/clone_circt.sh ./circt
BUILD_CIRCT_FROM_SOURCE=1 ./scripts/install_circt_bindings.sh ./circt
```

## Development commands

```bash
make lint
make typecheck
make test
make test-integration   # only if CIRCT is already installed
```

## CI

- `.github/workflows/ci.yml`
  - validates `3.14t` free-threaded runtime (`sys._is_gil_enabled() == False`),
  - runs lint, mypy, and non-integration tests,
  - intentionally avoids full CIRCT source builds.
- `.github/workflows/docker-base.yml`
  - manual workflow for building the heavy base image.

## Project structure

- `src/circt_hello/hello.py`: CIRCT hello-world builder.
- `src/circt_hello/cli.py`: CLI entrypoint.
- `tests/`: unit and integration tests.
- `scripts/`: bootstrap and image/build helpers.
- `docker/base/Dockerfile`: CIRCT-ready base image.
- `.devcontainer/`: Codespaces/devcontainer setup.
