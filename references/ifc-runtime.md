# Runtime determinístico IFC

## Componentes fixados

- Imagem: `openclaw-sandbox-ifc:0.8.5`
- IfcOpenShell: `ifcopenshell==0.8.5`
- IfcTester: `ifctester==0.8.5`
- Instalação: `python scripts/install_ifc_runtime.py`
- Verificação fail-closed: `python scripts/verify_ifc_runtime.py`
- Smoke test IFC/IDS: `python scripts/smoke_ifc_ids_runtime.py`, executado
  dentro da imagem fixada, sem rede e com a skill montada somente para leitura.

O inventário, relações, validação pós-exportação e IDS devem parar quando `safe_to_execute` não for `true`. Todo relatório deve registrar `tool_versions.ifcopenshell_version` e `tool_versions.ifctester_version` quando aplicável.

Depois de trocar a imagem configurada, executar `openclaw sandbox recreate --all`; os runtimes serão recriados no próximo uso.

Não recriar sandboxes quando a imagem efetiva já for a versão aprovada. Antes,
usar `openclaw sandbox list` e `openclaw sandbox explain --agent <id>` para
evitar interrupção desnecessária de sessões.

## Catálogo Notion

- `TOOL-IFCOS-001`: IfcOpenShell 0.8.5 — biblioteca oficial IFC.
- `TOOL-IFCT-001`: IfcTester 0.8.5 — auditoria IDS oficial.

Os dois registros começam como `Em revisão`. O RAG não deve utilizá-los como fonte aprovada até revisão humana mudar o status para `Aprovado`.

Fontes primárias:

- https://docs.ifcopenshell.org/ifcopenshell-python/installation.html
- https://docs.ifcopenshell.org/autoapi/ifctester/index.html
