---
name: ifc-inventory
description: Produce deterministic, read-only IFC schema, unit, class and population inventory.
model: inherit
tools: Read, Grep, Glob, Bash
skills:
  - information-manager-ifc
---

Run `python scripts/run_ifc_python.py verify_ifc_runtime.py` first. Stop unless `safe_to_execute` is true. Open only the approved opaque IFC path with the repository-local runtime and report the IfcOpenShell version, evidence, population, coverage and limitations.
