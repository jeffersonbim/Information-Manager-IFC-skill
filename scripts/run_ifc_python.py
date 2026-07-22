#!/usr/bin/env python3
"""Run an approved repository script with the Claude IFC virtualenv."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ALLOWED_SCRIPTS = {
    "verify_ifc_runtime.py",
    "ifc_mapping_validator.py",
    "parameter_mappings.py",
    "privacy_gate.py",
    "privacy_ingest.py",
}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if len(sys.argv) < 2 or Path(sys.argv[1]).name not in ALLOWED_SCRIPTS:
        print("BLOCK: script_not_allowlisted", file=sys.stderr)
        return 3
    python = root / ".ifc-venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not python.is_file():
        print("BLOCK: claude_ifc_runtime_not_installed", file=sys.stderr)
        return 3
    target = root / "scripts" / Path(sys.argv[1]).name
    return subprocess.run([str(python), str(target), *sys.argv[2:]], cwd=root, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
