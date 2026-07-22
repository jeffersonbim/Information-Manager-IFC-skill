---
name: information-manager-ifc
description: Orchestrate governed OpenBIM analysis for IFC, IDS, IDM, ISO 19650, bSDD, BCF and Revit-to-IFC mappings with local privacy preflight, deterministic IfcOpenShell evidence and specialist agents. Use for technical consultation or validation of IFC information requirements and mappings.
---

# Information Manager IFC for Claude Code

Treat the repository root `SKILL.md` as the canonical procedure and load only the referenced domain files needed for the task.

1. Require `scripts/privacy_ingest.py` and an opaque cleared path before reading a project artifact.
2. Stop unless both privacy decisions are `ALLOW` and `safe_to_forward` is true.
3. Run `scripts/verify_ifc_runtime.py`; stop unless `safe_to_execute` is true.
4. Delegate from the main coordinator only; specialists cannot spawn other agents.
5. Use deterministic scripts for findings and the model only for routing, explanation and consolidation.
6. Include `tool_versions`, evidence, coverage and limitations in every technical report.
7. Treat Notion as an approved consultative catalog, never as execution evidence or a project-results store.
