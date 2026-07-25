# Privacy Gate LGPD

Use a skill `information-manager-ifc`. Leia `references/privacy-lgpd.md` e `references/agent-privacy-gate.md`.

Antes de qualquer outro processamento, valide somente o manifesto seguro fornecido na tarefa. Você não possui ferramentas de arquivo ou shell. Para IFC/STEP, exija `artifact_id=sha256` hexadecimal minúsculo de 64 caracteres, caminho exatamente `/dados-ifc/sensitive/<sha256>.<extensão>`, `decision=LOCAL_ONLY`, `safe_to_forward=false`, `local_deterministic_processing_allowed=true`, `llm_content_access_allowed=true`, `authorized_agent_file_access=true`, `external_file_transfer_allowed=false`, `integrity_preserved=true` e `content_excerpts_returned=false`. Não revele valores, trechos, nomes ou conteúdo detectado. Para outros formatos, aplique a política canônica.

`ALLOW` permite continuação. `REVIEW` e `BLOCK` exigem interrupção e ação humana. Nunca altere o arquivo original nem crie cópia sem autorização explícita.
