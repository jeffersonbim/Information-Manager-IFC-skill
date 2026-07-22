#!/usr/bin/env python3
"""Build and verify the pinned OpenClaw IFC sandbox image."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE = "openclaw-sandbox-ifc:0.8.5"


def resolve_docker(finder=shutil.which, fallback_paths=None) -> dict[str, object]:
    discovered = finder("docker")
    if fallback_paths is None:
        fallback_paths = [r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"]
    candidates = [
        discovered,
        *fallback_paths,
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return {"status": "ready", "path": str(candidate)}
    return {
        "status": "blocked",
        "reason_code": "docker_cli_not_found",
        "next_action": "Inicie o Docker Desktop e adicione resources/bin ao PATH, ou reabra o terminal.",
    }


def run(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    subprocess.run(command, cwd=cwd, env=env, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Constrói e verifica o runtime IFC determinístico.")
    parser.add_argument("--image", default=IMAGE)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    docker = resolve_docker()
    if docker["status"] != "ready":
        print(json.dumps(docker, ensure_ascii=False))
        return 3
    executable = str(docker["path"])
    environment = os.environ.copy()
    docker_directory = str(Path(executable).parent)
    environment["PATH"] = docker_directory + os.pathsep + environment.get("PATH", "")
    build = [executable, "build", "-t", args.image]
    if args.no_cache:
        build.append("--no-cache")
    build.extend(["-f", "openclaw/Dockerfile.sandbox", "."])
    run(build, root, environment)
    run([
        executable, "run", "--rm", "--network", "none", args.image,
        "python", "-c",
        "import ifcopenshell,ifctester; print(ifcopenshell.version); assert ifcopenshell.version=='0.8.5'",
    ], root, environment)
    return 0


if __name__ == "__main__":
    sys.exit(main())
