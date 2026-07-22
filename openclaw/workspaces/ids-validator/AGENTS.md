# IDS Validator

Files under `/dados-ifc` must be accessed with `sandbox_exec` and treated as read-only.

Use `/skills/information-manager-ifc/references/parameter-mappings.md` only to map candidate names, datatypes, and scopes; do not infer IDS obligation from mapping presence. Never use IFC-SG mappings.
Execute `python /skills/information-manager-ifc/scripts/verify_ifc_runtime.py` first. Continue only with `safe_to_execute: true`, using the pinned IfcTester distributed with IfcOpenShell 0.8.5. Report both component versions. Use the `information-manager-ifc` skill and read `references/agent-ids-validator.md` plus `references/ids.md`. Execute only approved requirements. Treat zero applicability as a coverage warning unless justified.
