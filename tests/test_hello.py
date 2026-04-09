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
def test_build_hello_module_integration() -> None:
    circt = pytest.importorskip("circt")
    _ = circt
    mlir = build_hello_module()
    assert "hw.module @magic" in mlir
    assert "comb.xor" in mlir


@pytest.mark.integration
def test_build_hello_module_custom_integration() -> None:
    circt = pytest.importorskip("circt")
    _ = circt
    mlir = build_hello_module(HelloConfig(width=8, module_name="hello"))
    assert "hw.module @hello" in mlir
    assert "i8" in mlir
