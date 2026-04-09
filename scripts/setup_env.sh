#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY314T_PREFIX="${PY314T_PREFIX:-$HOME/.local/python-3.14t}"
PYTHON_BIN="${PYTHON_BIN:-$PY314T_PREFIX/bin/python3.14t}"
SKIP_BOOTSTRAP="${SKIP_BOOTSTRAP:-0}"

if [ "${1:-}" = "--skip-bootstrap" ]; then
  SKIP_BOOTSTRAP=1
fi

if [ "$SKIP_BOOTSTRAP" != "1" ] && [ ! -x "$PYTHON_BIN" ]; then
  "$ROOT_DIR/scripts/bootstrap_python314t.sh"
fi

if [ ! -x "$PYTHON_BIN" ]; then
  echo "python3.14t not found at: $PYTHON_BIN" >&2
  echo "Run scripts/bootstrap_python314t.sh first or set PYTHON_BIN." >&2
  exit 1
fi

if [ ! -d "$ROOT_DIR/.venv" ]; then
  "$PYTHON_BIN" -m venv "$ROOT_DIR/.venv"
fi

"$ROOT_DIR/.venv/bin/python" -m pip install --upgrade pip setuptools wheel
"$ROOT_DIR/.venv/bin/python" -m pip install -e "$ROOT_DIR[dev]"

cat <<EOF
Environment ready.
Activate with:
  source "$ROOT_DIR/.venv/bin/activate"
EOF
