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
        import importlib
        from types import SimpleNamespace

        import circt
        from circt.dialects import arc, comb, hw, hwarith, seq  # pyright: ignore
        from circt.ir import (  # pyright: ignore
            ArrayAttr,
            Attribute,
            Block,
            Context,
            DictAttr,
            FlatSymbolRefAttr,
            InsertionPoint,
            IntegerAttr,
            IntegerType,
            Location,
            Module,
            Operation,
            StringAttr,
            Type,
            Value,
        )
        from circt.passmanager import PassManager
        try:
            from circt.mlir.dialects import func  # pyright: ignore
        except ImportError:
            try:
                from circt.dialects import func  # pyright: ignore
            except ImportError:
                # Some CIRCT builds don't ship Python bindings for func.
                try:
                    func = importlib.import_module("circt.dialects._func_ops_gen")
                except ImportError:
                    func = SimpleNamespace(__name__="func")
    except ImportError as exc:  # pragma: no cover - exercised in tests via monkeypatch
        msg = (
            "CIRCT Python bindings are unavailable. Build/install from llvm/circt "
            "with: python -m pip install <path-to-circt>/lib/Bindings/Python"
        )
        raise CIRCTNotInstalledError(msg) from exc

    module_text_with_func = f"""
module {{
  func.func @mix_{cfg.module_name}(%lhs: i{cfg.width}, %rhs: i{cfg.width}) -> i{cfg.width} {{
    %0 = comb.xor %lhs, %rhs : i{cfg.width}
    %h1 = hwarith.constant 1 : ui{cfg.width}
    %h1_i = hwarith.cast %h1 : (ui{cfg.width}) -> i{cfg.width}
    %1 = comb.xor %0, %h1_i : i{cfg.width}
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
    %h1 = hwarith.constant 1 : ui{cfg.width}
    %h1_i = hwarith.cast %h1 : (ui{cfg.width}) -> i{cfg.width}
    %y = comb.xor %masked, %h1_i : i{cfg.width}
    hw.output %y : i{cfg.width}
  }}
}}
"""

    module_text_without_func = f"""
module {{
  arc.define @arc_gate(%lhs: i1, %rhs: i1) -> (i1) {{
    %0 = comb.and %lhs, %rhs : i1
    arc.output %0 : i1
  }}

  hw.module @{cfg.module_name}(in %a : i{cfg.width}, in %b : i{cfg.width}, out c : i{cfg.width}) {{
    %clk = seq.const_clock high
    %clk_i1 = seq.from_clock %clk
    %x = comb.xor %a, %b : i{cfg.width}
    %masked = comb.mux %clk_i1, %x, %a : i{cfg.width}
    %h1 = hwarith.constant 1 : ui{cfg.width}
    %h1_i = hwarith.cast %h1 : (ui{cfg.width}) -> i{cfg.width}
    %y = comb.xor %masked, %h1_i : i{cfg.width}
    hw.output %y : i{cfg.width}
  }}
}}
"""

    with Context() as ctx, Location.unknown():
        circt.register_dialects(ctx)
        register_func = getattr(func, "register_dialect", None)
        if callable(register_func):
            register_func(ctx)
        width_type = IntegerType.get_signless(cfg.width)
        width_mlir_type: Type = width_type
        if str(width_mlir_type) != f"i{cfg.width}":
            msg = "width type parsing mismatch"
            raise RuntimeError(msg)

        if func.__name__.endswith("_func_ops_gen"):
            func_name = "func"
        else:
            func_name = func.__name__.split(".")[-1]
        dialect_names = (
            hw.__name__.split(".")[-1],
            seq.__name__.split(".")[-1],
            comb.__name__.split(".")[-1],
            func_name,
            arc.__name__.split(".")[-1],
            hwarith.__name__.split(".")[-1],
        )
        func_probe_text = "module { func.func @__func_probe() { func.return } }"
        try:
            Module.parse(func_probe_text)
            func_dialect_usable = True
        except Exception as exc:
            if "Dialect `func' not found" not in str(exc):
                raise
            func_dialect_usable = False
        try:
            module = Module.parse(module_text_with_func)
        except Exception as exc:
            # Some CIRCT images omit the registered func dialect.
            if "Dialect `func' not found" not in str(exc):
                raise
            module = Module.parse(module_text_without_func)
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
                "dialects": ArrayAttr.get([StringAttr.get(name) for name in dialect_names]),
                "func_binding": StringAttr.get(func.__name__),
                "func_dialect_usable": IntegerAttr.get(
                    IntegerType.get_signless(1), int(func_dialect_usable)
                ),
                "arc_symbol": FlatSymbolRefAttr.get("arc_gate"),
                "note": note_attr,
            }
        )
        module.operation.attributes["circt_hello.meta"] = module_meta

        pm = PassManager.parse("builtin.module(cse)")
        pm.run(module.operation)
        return str(module)
