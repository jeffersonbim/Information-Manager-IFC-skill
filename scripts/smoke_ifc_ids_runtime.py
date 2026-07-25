#!/usr/bin/env python3
"""Autocontained acceptance test for the pinned IFC/IDS runtime."""

from __future__ import annotations

import json
import tempfile
from importlib.metadata import version
from pathlib import Path

import ifcopenshell
import ifcopenshell.guid
from ifctester import ids


def create_wall(model: ifcopenshell.file, name: str):
    return model.create_entity(
        "IfcWall",
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )


def main() -> int:
    model = ifcopenshell.file(schema="IFC4")
    create_wall(model, "WALL-PASS")
    create_wall(model, "WALL-FAIL")

    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "runtime-smoke.ifc"
        model.write(path)
        reopened = ifcopenshell.open(path)

        specification = ids.Specification(
            name="Wall name smoke test",
            minOccurs=1,
            maxOccurs="unbounded",
            ifcVersion=["IFC4"],
        )
        specification.applicability.append(ids.Entity(name="IFCWALL"))
        specification.requirements.append(
            ids.Attribute(name="Name", value="WALL-PASS")
        )
        suite = ids.Ids(title="Pinned runtime smoke test")
        suite.specifications.append(specification)
        suite.validate(reopened)

        applicable = len(specification.applicable_entities)
        passed = len(specification.passed_entities)
        failed = len(specification.failed_entities)
        result = {
            "status": "ready"
            if applicable == 2 and passed == 1 and failed == 1
            else "blocked",
            "safe_to_execute": (
                applicable == 2 and passed == 1 and failed == 1
            ),
            "ifcopenshell_version": ifcopenshell.version,
            "ifctester_version": version("ifctester"),
            "schema": reopened.schema,
            "applicable": applicable,
            "passed": passed,
            "failed": failed,
            "coverage_zero_zero": applicable == 0,
        }
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0 if result["safe_to_execute"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
