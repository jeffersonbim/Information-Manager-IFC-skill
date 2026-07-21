# Privacy Gate LGPD

Use a skill `information-manager-ifc`. Leia `references/privacy-lgpd.md` e `references/agent-privacy-gate.md`.

Antes de qualquer outro processamento, valide somente o manifesto seguro fornecido na tarefa. Você não possui ferramentas de arquivo ou shell. Exija `artifact_id=sha256` hexadecimal minúsculo de 64 caracteres, caminho exatamente `/dados-ifc/cleared/<sha256>.<extensão permitida>`, `decision=ALLOW`, `safe_to_forward=true` e `content_excerpts_returned=false`. O stem deve ser exatamente o hash. Não revele valores, trechos, nomes ou conteúdo detectado. Retorne apenas a decisão e os campos seguros.

`ALLOW` permite continuação. `REVIEW` e `BLOCK` exigem interrupção e ação humana. Nunca altere o arquivo original nem crie cópia sem autorização explícita.
