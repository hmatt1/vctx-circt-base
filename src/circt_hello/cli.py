"""CLI for generating CIRCT hello-world MLIR."""

from __future__ import annotations

import argparse

from circt_hello.hello import HelloConfig, build_hello_module


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate CIRCT hello-world MLIR")
    parser.add_argument("--width", type=int, default=42, help="Bit width for ports")
    parser.add_argument(
        "--module-name",
        type=str,
        default="magic",
        help="Name of the generated hw.module",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    config = HelloConfig(width=args.width, module_name=args.module_name)
    print(build_hello_module(config))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
