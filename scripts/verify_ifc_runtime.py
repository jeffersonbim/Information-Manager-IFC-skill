#!/usr/bin/env python3
"""Fail-closed capability check for deterministic IFC execution."""

from __future__ import annotations

import importlib
import importlib.metadata
import json
import sys
from collections.abc import Callable
from typing import Any


REQUIRED_IFCOPENSHELL_VERSION = "0.8.5"
REQUIRED_IFCTESTER_VERSION = "0.8.5"


def _version(module: Any, distribution: str) -> str:
    declared = getattr(module, "version", getattr(module, "__version__", None))
    if declared is not None:
        return str(declared)
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def verify_runtime(importer: Callable[[str], Any] = importlib.import_module) -> dict[str, object]:
    components: dict[str, dict[str, object]] = {}
    reasons: list[str] = []
    for name in ("ifcopenshell", "ifctester"):
        try:
            module = importer(name)
            components[name] = {"available": True, "version": _version(module, name)}
        except (ImportError, ModuleNotFoundError):
            components[name] = {"available": False, "version": None}
            reasons.append(f"{name}_unavailable")

    required = {
        "ifcopenshell": REQUIRED_IFCOPENSHELL_VERSION,
        "ifctester": REQUIRED_IFCTESTER_VERSION,
    }
    for name, expected in required.items():
        if not components[name]["available"]:
            continue
        installed = components[name]["version"]
        if installed in (None, "unknown"):
            reasons.append(f"{name}_version_unknown")
        elif installed != expected:
            reasons.append(f"{name}_version_mismatch")

    ready = not reasons
    return {
        "status": "ready" if ready else "blocked",
        "safe_to_execute": ready,
        "required_ifcopenshell_version": REQUIRED_IFCOPENSHELL_VERSION,
        "required_ifctester_version": REQUIRED_IFCTESTER_VERSION,
        "components": components,
        "reason_codes": reasons,
    }


def main() -> int:
    result = verify_runtime()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["safe_to_execute"] else 3


if __name__ == "__main__":
    sys.exit(main())
