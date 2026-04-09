#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <path-to-circt-checkout>" >&2
  exit 1
fi

CIRCT_DIR="$(cd "$1" && pwd)"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ ! -d "$CIRCT_DIR/lib/Bindings/Python" ]; then
  echo "Expected CIRCT Python bindings at $CIRCT_DIR/lib/Bindings/Python" >&2
  exit 1
fi

PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/.venv/bin/python}"
if [ ! -x "$PYTHON_BIN" ]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-$HOME/.local/python-3.14t/bin/python3.14t}"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "No usable Python found. Run scripts/setup_env.sh first." >&2
  exit 1
fi

export CMAKE_GENERATOR="${CMAKE_GENERATOR:-Ninja}"
"$PYTHON_BIN" -m pip install "$CIRCT_DIR/lib/Bindings/Python"
"$PYTHON_BIN" -c 'import circt; print("CIRCT import OK")'
