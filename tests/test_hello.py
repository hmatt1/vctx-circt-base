from __future__ import annotations

import builtins
from typing import Any, cast

import pytest

from circt_hello.hello import (
    CIRCTNotInstalledError,
    HelloConfig,
    _validate_config,
    build_hello_module,
)


def test_validate_config_rejects_invalid_width() -> None:
    with pytest.raises(ValueError, match="positive"):
        _validate_config(HelloConfig(width=0, module_name="magic"))


def test_validate_config_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        _validate_config(HelloConfig(width=42, module_name=""))


def test_build_hello_module_errors_when_circt_unavailable() -> None:
    original_import = cast(Any, builtins.__import__)

    def import_hook(
        name: str,
        globals_: dict[str, Any] | None = None,
        locals_: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name == "circt" or name.startswith("circt."):
            raise ImportError("missing circt")
        return original_import(name, globals_, locals_, fromlist, level)

    with pytest.MonkeyPatch.context() as monkeypatch:
        monkeypatch.setattr(builtins, "__import__", import_hook)
        with pytest.raises(CIRCTNotInstalledError, match="CIRCT Python bindings"):
            build_hello_module()


@pytest.mark.integration
def test_circt_real_dialect_ops_integration() -> None:
    import circt
    from circt.dialects import comb, hw
    from circt.ir import Context, InsertionPoint, IntegerType, Location, Module

    with Context() as ctx, Location.unknown():
        circt.register_dialects(ctx)
        module = Module.create()
        i4 = IntegerType.get_signless(4)
        with InsertionPoint(module.body):
            def body_builder(op: Any) -> dict[str, Any]:
                xor = comb.XorOp.create(op.a, op.b)
                return {"c": xor}

            hw.HWModuleOp(
                name="integration_smoke",
                input_ports=[("a", i4), ("b", i4)],
                output_ports=[("c", i4)],
                body_builder=body_builder,
            )

    mlir = str(module)
    assert "hw.module @integration_smoke" in mlir
    assert "comb.xor" in mlir


@pytest.mark.integration
def test_build_hello_module_integration() -> None:
    mlir = build_hello_module()
    assert "hw.module @magic" in mlir
    assert "comb.xor" in mlir
    assert ("func.func @mix_magic" in mlir) or ('"func"' in mlir)
    assert "arc.define @arc_gate" in mlir
    assert "seq.const_clock" in mlir
    assert "hwarith.cast" in mlir
    assert '"circt_hello.meta"' in mlir


@pytest.mark.integration
def test_build_hello_module_custom_integration() -> None:
    mlir = build_hello_module(HelloConfig(width=8, module_name="hello"))
    assert "hw.module @hello" in mlir
    assert "i8" in mlir
    assert ("func.func @mix_hello" in mlir) or ('"func"' in mlir)
