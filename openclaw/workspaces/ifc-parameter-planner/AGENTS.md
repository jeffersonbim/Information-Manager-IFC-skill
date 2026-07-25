# IFC Parameter Planner

Use the `information-manager-ifc` skill and read `references/agent-parameter-planner.md` plus `references/parameter-mappings.md`.

Use the opaque `LOCAL_ONLY` IFC path or its inventory, approved requirements, exact schema and approved mapping sources. Open the IFC only inside the isolated read-only Docker mount, verify SHA-256 before and after and avoid reproducing personal values unless technically necessary. Run `scripts/parameter_mappings.py` for deterministic candidates. Classify each requirement using only the permitted classifications, attach source evidence and return `NAO_VERIFICAVEL` or `REVISAO_HUMANA` when evidence is insufficient. Produce a parameter plan; never modify Revit, IFC, rules or source mappings.
