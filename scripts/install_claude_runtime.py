#!/usr/bin/env python3
"""Create a repository-local, pinned IFC runtime for Claude Code."""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path


def venv_python(root: Path) -> Path:
    windows = root / ".ifc-venv" / "Scripts" / "python.exe"
    return windows if sys.platform == "win32" else root / ".ifc-venv" / "bin" / "python"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    environment = root / ".ifc-venv"
    venv.EnvBuilder(with_pip=True, clear=False).create(environment)
    python = venv_python(root)
    subprocess.run([
        str(python), "-m", "pip", "install", "--disable-pip-version-check",
        "ifcopenshell==0.8.5", "ifctester==0.8.5",
    ], cwd=root, check=True)
    return subprocess.run([str(python), "scripts/verify_ifc_runtime.py"], cwd=root, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
