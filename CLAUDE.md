# Information Manager IFC — Claude Code

Use `.claude/skills/information-manager-ifc/SKILL.md` for every IFC, IDS, IDM, ISO 19650, bSDD, BCF or Revit-to-IFC task.

- When a compatible `Template_Consulta_Parametros_Revit_IFC.xlsx` is attached, treat it as an automatic intake trigger: validate it with `scripts/template_intake.py` and start read-only mapping triage only for rows with all mandatory fields.

- Keep IFC inputs local and read-only.
- Treat every IFC/STEP as sensitive. Require `LOCAL_ONLY`, byte-for-byte SHA-256 integrity and an isolated read-only Docker mount. Authorized IFC agents may read the intact artifact; never transfer it to unapproved external services.
- Run deterministic tools before interpretation.
- Never declare compliance from model inference.
- Record source, coverage, limitations and tool versions.
- Do not write to Notion except when the user explicitly requests knowledge curation.
- On corporate machines, do not run the coordinator or specialists directly on the host. Follow `references/agent-runtime-security.md`.
- Do not claim that tools running in Docker isolate an agent that is still running on the host.
- Keep OpenClaw in service until the replacement runtime passes the documented security and deterministic-equivalence tests.
- Preserve the Claude–MCP synergy: analysis agents produce the parameter plan and SMR; only the Claude executor may use Revit MCP, with read-only inspection before approval and scoped writes afterward.
- Keep the full `revit-mcp-server` tool catalog available to the Claude executor. Tool availability is approved globally, but every mutating call still requires an approved SMR covering its concrete target and arguments.
