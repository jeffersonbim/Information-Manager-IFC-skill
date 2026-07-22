#!/usr/bin/env python3
"""Fail-closed capability check for deterministic IFC execution."""

from __future__ import annotations

import importlib
import json
import sys
from collections.abc import Callable
from typing import Any


REQUIRED_IFCOPENSHELL_VERSION = "0.8.5"


def _version(module: Any) -> str:
    return str(getattr(module, "version", getattr(module, "__version__", "unknown")))


def verify_runtime(importer: Callable[[str], Any] = importlib.import_module) -> dict[str, object]:
    components: dict[str, dict[str, object]] = {}
    reasons: list[str] = []
    for name in ("ifcopenshell", "ifctester"):
        try:
            module = importer(name)
            components[name] = {"available": True, "version": _version(module)}
        except (ImportError, ModuleNotFoundError):
            components[name] = {"available": False, "version": None}
            reasons.append(f"{name}_unavailable")

    installed = components["ifcopenshell"]["version"]
    if installed not in (None, "unknown", REQUIRED_IFCOPENSHELL_VERSION):
        reasons.append("ifcopenshell_version_mismatch")

    ready = not reasons
    return {
        "status": "ready" if ready else "blocked",
        "safe_to_execute": ready,
        "required_ifcopenshell_version": REQUIRED_IFCOPENSHELL_VERSION,
        "components": components,
        "reason_codes": reasons,
    }


def main() -> int:
    result = verify_runtime()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["safe_to_execute"] else 3


if __name__ == "__main__":
    sys.exit(main())
