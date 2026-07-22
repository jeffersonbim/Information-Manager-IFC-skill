#!/usr/bin/env python3
"""Build and verify the pinned OpenClaw IFC sandbox image."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


IMAGE = "openclaw-sandbox-ifc:0.8.5"


def run(command: list[str], cwd: Path) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Constrói e verifica o runtime IFC determinístico.")
    parser.add_argument("--image", default=IMAGE)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    build = ["docker", "build", "-t", args.image]
    if args.no_cache:
        build.append("--no-cache")
    build.extend(["-f", "openclaw/Dockerfile.sandbox", "."])
    run(build, root)
    run([
        "docker", "run", "--rm", "--network", "none", args.image,
        "python", "-c",
        "import ifcopenshell,ifctester; print(ifcopenshell.version); assert ifcopenshell.version=='0.8.5'",
    ], root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
