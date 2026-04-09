from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "src")
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "circt_hello.cli",
            *args,
        ],
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_without_circt_fails_cleanly() -> None:
    if importlib.util.find_spec("circt"):
        pytest.skip("CIRCT is installed; missing-circt path not applicable")

    result = _run_cli([])
    assert result.returncode != 0
    assert "CIRCT Python bindings are unavailable" in result.stderr


@pytest.mark.integration
def test_cli_integration() -> None:
    pytest.importorskip("circt")
    result = _run_cli(["--width", "16", "--module-name", "demo"])
    assert result.returncode == 0
    assert "hw.module @demo" in result.stdout
    assert "i16" in result.stdout
