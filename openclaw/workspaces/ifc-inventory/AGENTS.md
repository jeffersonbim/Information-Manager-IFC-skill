# IFC Inventory

Files under `/dados-ifc` must be accessed with `sandbox_exec` and treated as read-only.

Use `/skills/information-manager-ifc/references/parameter-mappings.md` and `/skills/information-manager-ifc/scripts/parameter_mappings.py` when inventorying mapped Revit/IFC or COBie properties. Never use IFC-SG mappings.
Before opening any IFC, execute `python /skills/information-manager-ifc/scripts/verify_ifc_runtime.py`. Stop with `status: error` when `safe_to_execute` is not `true`; never replace missing IfcOpenShell with model inference.
Use the `information-manager-ifc` skill and read `references/agent-inventory.md`. Perform only deterministic, read-only inventory. Return the common JSON contract with evidence, population, limitations, next actions and `tool_versions.ifcopenshell_version`.
