"""CIRCT hello-world builder."""

from __future__ import annotations

from dataclasses import dataclass


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
    """Build a substantial single-module CIRCT MLIR example."""

    cfg = config or HelloConfig()
    _validate_config(cfg)

    try:
        import circt
        from circt.ir import (  # pyright: ignore
            Context,
            InsertionPoint,
            IntegerType,
            Location,
            Module,
            Value,
            Type,
            Block,
            Operation,
            IntegerAttr,
            DictAttr,
            StringAttr,
            ArrayAttr,
            Attribute,
            FlatSymbolRefAttr,
        )
        from circt.dialects import hw, seq, comb, func, arc, hwarith  # pyright: ignore
        from circt.passmanager import PassManager
    except ImportError as exc:  # pragma: no cover - exercised in tests via monkeypatch
        msg = (
            "CIRCT Python bindings are unavailable. Build/install from llvm/circt "
            "with: python -m pip install <path-to-circt>/lib/Bindings/Python"
        )
        raise CIRCTNotInstalledError(msg) from exc

    module_text = f"""
module {{
  func.func @mix_{cfg.module_name}(%lhs: i{cfg.width}, %rhs: i{cfg.width}) -> i{cfg.width} {{
    %0 = comb.xor %lhs, %rhs : i{cfg.width}
    %1 = hwarith.cast %0 : (i{cfg.width}) -> i{cfg.width}
    func.return %1 : i{cfg.width}
  }}

  arc.define @arc_gate(%lhs: i1, %rhs: i1) -> (i1) {{
    %0 = comb.and %lhs, %rhs : i1
    arc.output %0 : i1
  }}

  hw.module @{cfg.module_name}(in %a : i{cfg.width}, in %b : i{cfg.width}, out c : i{cfg.width}) {{
    %clk = seq.const_clock high
    %clk_i1 = seq.from_clock %clk
    %x = comb.xor %a, %b : i{cfg.width}
    %masked = comb.mux %clk_i1, %x, %a : i{cfg.width}
    %y = hwarith.cast %masked : (i{cfg.width}) -> i{cfg.width}
    hw.output %y : i{cfg.width}
  }}
}}
"""

    with Context() as ctx, Location.unknown():
        circt.register_dialects(ctx)
        width_type = IntegerType.get_signless(cfg.width)
        parsed_width_type: Type = Type.parse(f"i{cfg.width}")
        if str(parsed_width_type) != str(width_type):
            msg = "width type parsing mismatch"
            raise RuntimeError(msg)

        # Keep explicit references to all requested dialect modules.
        dialect_modules = (hw, seq, comb, func, arc, hwarith)
        module = Module.parse(module_text)
        top_block: Block = module.body
        top_ops = [op for op in top_block.operations]
        if not top_ops:
            msg = "expected at least one top-level operation"
            raise RuntimeError(msg)

        first_op: Operation = top_ops[0]
        first_arg: Value = first_op.regions[0].blocks[0].arguments[0]
        _ = first_arg.type
        with InsertionPoint(top_block):
            pass

        note_attr: Attribute = Attribute.parse('"substantial hello world"')
        module_meta = DictAttr.get(
            {
                "module_name": StringAttr.get(cfg.module_name),
                "width": IntegerAttr.get(IntegerType.get_signless(32), cfg.width),
                "dialects": ArrayAttr.get(
                    [StringAttr.get(mod.__name__.split(".")[-1]) for mod in dialect_modules]
                ),
                "arc_symbol": FlatSymbolRefAttr.get("arc_gate"),
                "note": note_attr,
            }
        )
        module.operation.attributes["circt_hello.meta"] = module_meta

        pm = PassManager.parse("builtin.module(cse)")
        pm.run(module.operation)
        return str(module)
