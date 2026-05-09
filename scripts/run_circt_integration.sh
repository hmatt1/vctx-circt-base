#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${1:-python3.14t}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python binary not found: $PYTHON_BIN" >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
import sys
import sysconfig

print(sys.version)
print("Py_GIL_DISABLED=", sysconfig.get_config_var("Py_GIL_DISABLED"))
print("gil_enabled=", sys._is_gil_enabled())

assert sys.version_info[:2] == (3, 14)
assert sysconfig.get_config_var("Py_GIL_DISABLED") == 1
assert hasattr(sys, "_is_gil_enabled")
assert not sys._is_gil_enabled()
PY

"$PYTHON_BIN" - <<'PY'
import circt
from circt.dialects import comb, hw
from circt.ir import Context, InsertionPoint, IntegerType, Location, Module

with Context() as ctx, Location.unknown():
    circt.register_dialects(ctx)
    module = Module.create()
    i1 = IntegerType.get_signless(1)
    with InsertionPoint(module.body):
        def body_builder(op):
            xor = comb.XorOp.create(op.a, op.b)
            return {"c": xor}

        hw.HWModuleOp(
            name="ci_smoke",
            input_ports=[("a", i1), ("b", i1)],
            output_ports=[("c", i1)],
            body_builder=body_builder,
        )
    print(module)
PY
