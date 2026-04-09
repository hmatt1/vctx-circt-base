"""CIRCT hello-world builder."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HelloConfig:
    """Configuration for the hello-world hardware module."""

    width: int = 42
    module_name: str = "magic"


class CIRCTNotInstalledError(RuntimeError):
    """Raised when CIRCT Python bindings are not installed."""


def _validate_config(config: HelloConfig) -> None:
    if config.width <= 0:
        msg = "width must be a positive integer"
        raise ValueError(msg)
    if not config.module_name:
        msg = "module_name must be non-empty"
        raise ValueError(msg)


def build_hello_module(config: HelloConfig | None = None) -> str:
    """Build a tiny CIRCT module and return its MLIR text.

    This mirrors CIRCT's official Python bindings example while keeping
    the function easy to test and reuse.
    """

    cfg = config or HelloConfig()
    _validate_config(cfg)

    try:
        import circt
        from circt.dialects import comb, hw
        from circt.ir import Context, InsertionPoint, IntegerType, Location, Module
    except ImportError as exc:  # pragma: no cover - exercised in tests via monkeypatch
        msg = (
            "CIRCT Python bindings are unavailable. Build/install from llvm/circt "
            "with: python -m pip install <path-to-circt>/lib/Bindings/Python"
        )
        raise CIRCTNotInstalledError(msg) from exc

    with Context() as ctx, Location.unknown():
        circt.register_dialects(ctx)
        width_type = IntegerType.get_signless(cfg.width)
        module = Module.create()

        with InsertionPoint(module.body):

            def body_builder(op: Any) -> dict[str, Any]:
                xor = comb.XorOp.create(op.a, op.b)
                return {"c": xor}

            hw.HWModuleOp(
                name=cfg.module_name,
                input_ports=[("a", width_type), ("b", width_type)],
                output_ports=[("c", width_type)],
                body_builder=body_builder,
            )

        return str(module)
