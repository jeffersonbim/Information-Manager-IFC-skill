# IFC Mapping Validator

Use the `information-manager-ifc` skill and read `references/agent-mapping-validator.md`.

Files under `/dados-ifc` and `/skills/information-manager-ifc` are read-only. Run `/skills/information-manager-ifc/scripts/ifc_mapping_validator.py` against an approved, versioned rules JSON. Never invent category mappings. Without authoring CSV, report source-parameter completeness as `NAO_VERIFICAVEL`. Without shared `GlobalId`, do not claim source-to-IFC reconciliation.
