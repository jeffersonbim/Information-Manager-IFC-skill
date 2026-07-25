---
name: information-manager-ifc
description: Orchestrate governed OpenBIM analysis for IFC, IDS, IDM, ISO 19650, bSDD, BCF and Revit-to-IFC mappings with local privacy preflight, deterministic IfcOpenShell evidence and specialist agents. Use for technical consultation or validation of IFC information requirements and mappings.
---

# Information Manager IFC for Claude Code

Treat the repository root `SKILL.md` as the canonical procedure and load only the referenced domain files needed for the task.

1. Before each technical gate, read `references/gates-questionnaire.md`, ask the user the five questions for the current gate and validate the recorded answers with `scripts/gate_questionnaire.py`. Do not infer missing answers or continue while the questionnaire is `BLOCKED`.
2. Treat every IFC/STEP as sensitive. Require `scripts/privacy_ingest.py`, an opaque sensitive path and byte-for-byte SHA-256 integrity before processing.
3. For IFC/STEP, require `LOCAL_ONLY`. Authorized IFC workers may read the intact opaque snapshot inside the isolated read-only Docker mount; verify SHA-256 before and after. Never transfer the file to Notion, bSDD or unrelated external APIs. For other formats, require `ALLOW` and `safe_to_forward=true`.
3. Install once with `python scripts/install_claude_runtime.py`, then run `python scripts/run_ifc_python.py verify_ifc_runtime.py`; stop unless `safe_to_execute` is true.
4. Delegate from the main coordinator only; specialists cannot spawn other agents.
5. Use deterministic scripts for findings and the model only for routing, explanation and consolidation.
6. Include `tool_versions`, evidence, coverage and limitations in every technical report.
7. Treat Notion as an approved consultative catalog, never as execution evidence or a project-results store.
8. On corporate machines, read `references/agent-runtime-security.md` and stop if Claude Code or any specialist would run on the host. Dockerizing only IFC tools is not sufficient.
9. Keep OpenClaw as the authorized runtime until the containerized Claude agent runtime passes the documented isolation, deterministic-equivalence and human-approval gates.
10. Use Revit MCP only through the Claude executor contract in `references/revit-mcp-execution.md`; analysis workers never receive Revit MCP tools, and writes require an explicitly approved SMR.
