# CIRCT Hello (Python 3.14t)

A practical, minimal, robust starter project that generates a tiny CIRCT module from Python using the official CIRCT bindings pattern.

## What this gives you

- Python package + CLI (`circt-hello`) that prints MLIR.
- Python `3.14t` (free-threaded CPython) bootstrap scripts.
- Tests that run without CIRCT installed, plus integration tests when CIRCT is present.
- GitHub Actions CI (lint, typecheck, unit test on `3.14t`).
- Optional integration workflow that builds/installs CIRCT bindings.
- GitHub Codespaces devcontainer pinned to `3.14t`.
- Reusable Docker base image with CIRCT preinstalled.

## Quick start (local)

### 1) Bootstrap Python 3.14t + venv

```bash
make setup
```

This will:
- build/install `python3.14t` under `~/.local/python-3.14t` if missing,
- create `.venv`,
- install this project in editable mode with dev dependencies.

Activate your env:

```bash
source .venv/bin/activate
python -VV
```

You should see `3.14` and a free-threaded build.

### 2) Install CIRCT bindings

Clone CIRCT and install from `lib/Bindings/Python`:

```bash
git clone https://github.com/llvm/circt.git
cd circt
git submodule update --init --recursive
cd ..
./scripts/install_circt_bindings.sh ./circt
```

### 3) Run hello world

```bash
make run
```

Or with custom args:

```bash
.venv/bin/circt-hello --width 8 --module-name hello
```

## Expected output

You should get MLIR with a hardware module that XORs two inputs, similar to:

- `hw.module @magic(...)`
- `comb.xor`

## Development commands

```bash
make lint
make typecheck
make test
make test-integration   # requires circt bindings installed
```

## CI

- `.github/workflows/ci.yml`
  - `lint-type-test`: runs on push/PR using `actions/setup-python` with `3.14t`.
  - `integration-circt`: manual (`workflow_dispatch`) because CIRCT source build/install is heavy.
- `.github/workflows/docker-base.yml`
  - manually builds the Docker base image.

## Codespaces

- `.devcontainer/` compiles Python `3.14t` inside container and runs `./scripts/setup_env.sh --skip-bootstrap` on create.
- Recommended VS Code extensions included (Python, Pylance, Ruff).

## Docker base image

Build locally:

```bash
./scripts/build_base_image.sh
```

Image includes:
- Ubuntu 24.04 build toolchain,
- Python `3.14t`,
- CIRCT repo checkout + installed Python bindings.

## Project structure

- `src/circt_hello/hello.py`: CIRCT hello-world builder.
- `src/circt_hello/cli.py`: CLI entrypoint.
- `tests/`: unit and integration tests.
- `scripts/`: bootstrap/install helpers.
- `docker/base/Dockerfile`: CIRCT-ready base image.
- `.devcontainer/`: Codespaces/devcontainer setup.

## Notes

- CIRCT bindings are installed from source (official path) rather than a stable prebuilt PyPI package.
- Unit tests are designed to remain useful even when CIRCT is not installed.
