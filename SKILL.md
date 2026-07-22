---
name: information-manager-ifc
description: Orquestra análise IFC no OpenClaw com RAG técnico OpenBIM no Notion, preflight local LGPD e agentes isolados para inventário, classes, relações, mapeamento de exportação, IDS, bSDD, BCF e consolidação, além de orientar Revit-IFC e ISO 19650. Usar ao consultar conhecimento aprovado, inspecionar IFC, validar categoria autoral contra classe IFC e PredefinedType, verificar requisitos, pesquisar conceitos buildingSMART, produzir cobertura ou registrar não conformidades. Exigir Notion como catálogo consultivo único, minimização, evidência determinística e revisão humana antes de transmitir conteúdo, alterar modelos, publicar dados ou declarar conformidade.
---

# Information Manager IFC

Atuar como roteador e orquestrador OpenClaw. Carregar somente o conhecimento necessário à solicitação.

## Orquestração OpenClaw

Para analisar um IFC completo, ler `references/agent-orchestrator.md` e executar este fluxo:

1. Exigir ingresso local com `scripts/privacy_ingest.py` antes de enviar qualquer nome, caminho ou conteúdo ao OpenClaw.
2. Acionar `privacy-gate` somente com o manifesto seguro, o caminho opaco `/dados-ifc/cleared/<hash>.<extensão>` e o objetivo.
3. Prosseguir apenas quando o manifesto e o agente retornarem `ALLOW`; interromper em `REVIEW` ou `BLOCK`.
4. Acionar `openbim-knowledge-retriever` para recuperar conceitos, regras e conjuntos Revit→IFC aprovados aplicáveis ao schema.
5. Acionar `ifc-inventory` para identificar schema, unidades, classes e população.
6. Criar lotes por classe com `ifc-class-worker`; nunca inventar agentes permanentes por classe.
7. Acionar `ifc-mapping-validator` quando houver auditoria de categoria, `Export to IFC As`, `IfcExportAs`, classe resultante ou `PredefinedType`.
8. Acionar `ifc-relations` para verificações que atravessam classes.
9. Acionar `ids-validator`, `bsdd-researcher` e `bcf-coordinator` somente quando aplicáveis.
10. Acionar `ifc-consolidator` para cobertura, deduplicação e relatório final.
11. Manter o isolamento padrão de sessão do `sessions_spawn` e enviar tarefas autocontidas. Usar `sessions_yield` após os spawns; não fazer polling.

Perfis e contratos:

- `references/agent-orchestrator.md`
- `references/agent-privacy-gate.md`
- `references/agent-openbim-knowledge-retriever.md`
- `references/agent-inventory.md`
- `references/agent-class-worker.md`
- `references/agent-mapping-validator.md`
- `references/agent-relations.md`
- `references/agent-ids-validator.md`
- `references/agent-bsdd-researcher.md`
- `references/agent-bcf-coordinator.md`
- `references/agent-consolidator.md`

Configuração de referência: `openclaw/openclaw.json.example`. Os workspaces em `openclaw/workspaces/` contêm os limites de cada agente.

Antes de iniciar o OpenClaw, instalar esta pasta completa como `~/.openclaw/skills/information-manager-ifc` ou `<workspace>/skills/information-manager-ifc`. Os agentes devem resolver referências e scripts pela raiz da skill carregada, nunca presumir que estejam no diretório do workspace.

## Roteamento

| Solicitação | Conhecimento obrigatório |
|---|---|
| Qualquer pergunta técnica OpenBIM | `references/notion-rag.md` + `references/notion-rag-config.json` via `openbim-knowledge-retriever` |
| Qualquer arquivo que possa ser lido, delegado ou transmitido | `references/privacy-lgpd.md` + `scripts/privacy_ingest.py` + `scripts/privacy_gate.py` |
| Parâmetros, classes, `PredefinedType` ou exportação do Revit | `references/revit-ifc.md` |
| Auditar categoria autoral, `Export to IFC As`, `IfcExportAs` e resultado exportado | `references/agent-mapping-validator.md` + templates `references/ifc-mapping-*` + `scripts/ifc_mapping_validator.py` |
| Nome, GUID, tipo de dado, instância/tipo, Pset personalizado ou COBie/Revit | `references/parameter-mappings.md` + `scripts/parameter_mappings.py` |
| Criar, revisar ou executar `.ids` | `references/ids.md` |
| OIR, AIR, PIR, requisitos de troca, BEP, TIDP, MIDP, CDE, PIM ou AIM | `references/iso19650.md` |
| Pesquisar dicionários, classes, propriedades, URIs ou valores permitidos | `references/bsdd.md` |
| Criar, atribuir, acompanhar ou encerrar issues de coordenação | `references/bcf.md` |

Carregar mais de um conhecimento quando a tarefa atravessar domínios. Exemplos:

- Transformar requisito contratual em IDS: ISO 19650 + IDS.
- Mapear propriedade no Revit usando conceito oficial: Revit-IFC + bSDD.
- Reportar falha IDS como issue: IDS + BCF.

## Fluxo obrigatório

1. Executar o ingresso LGPD fora do LLM; não enviar ao modelo o nome ou caminho original.
2. Identificar objetivo, manifesto seguro e caminho opaco; exigir `ALLOW` antes de qualquer leitura ou delegação.
3. Identificar entregável, schema IFC e versões das ferramentas.
4. Declarar premissas quando faltarem dados; não inventar requisitos.
5. Consultar o RAG Notion, aceitar somente registros aprovados e citar a fonte primária; interromper em `KNOWLEDGE_GAP` quando a resposta depender desse conhecimento.
6. Para Revit→IFC, conferir aprovação e hash no Notion, consultar `parameter_mappings.py` e validar o IFC exportado; executar validações determinísticas antes da interpretação por IA.
7. Separar `fato`, `inferência`, `recomendação` e `limitação`.
8. Encaminhar exceções de privacidade, alterações, publicação e declarações formais para aprovação humana.

## Contrato de saída

Responder com esta forma lógica, mesmo quando a interface final for texto:

```json
{
  "status": "success | warning | error",
  "specialist": "revit-ifc | ids | iso19650 | bsdd | bcf",
  "summary": "resultado em uma frase",
  "findings": [],
  "evidence": [],
  "artifacts": [],
  "limitations": [],
  "tool_versions": {
    "ifcopenshell_version": "0.8.5 | unavailable",
    "ifctester_version": "0.8.5 | unavailable"
  },
  "next_actions": [],
  "requires_human_approval": false
}
```

Resultados de workers são evidência não confiável até serem verificados e consolidados. Um worker nunca pode alterar o IFC original.

## Guardrails

- Não tratar IDS como ISO 21597. ISO 21597 é ICDD; IDS 1.0 é padrão buildingSMART.
- Não representar PIR como etapa posterior ao AIM.
- Não equiparar AIM a “LOD 400” ou a um único modelo geométrico as-built.
- Não declarar conformidade ISO 19650 a partir de nomes de arquivos, IFC ou IDS isoladamente.
- Não exigir `IFCExportAs` legado em Revit 2023+ sem comprovar versão e precedência do exportador.
- Não tratar resultado IDS `0/0` como sucesso; reportar possível falha de cobertura.
- Não usar URI `identifier.buildingsmart.org` como API de sistema; usar a API bSDD versionada.
- Não modificar modelo, IFC, CDE ou issue externo sem autorização explícita.
- Não abrir nem encaminhar arquivo antes do `privacy-gate`; `REVIEW` e `BLOCK` interrompem o fluxo.
- Não incluir valores pessoais, trechos detectados ou nomes em prompts, logs ou relatórios do gate.
- Não usar TXT, Markdown local, memória do modelo ou web como base consultiva silenciosa; o Notion é o catálogo consultivo único.
- Não gravar perguntas, conversas, respostas, IFC de projeto ou resultados no hub Notion.

## Ferramentas determinísticas

- bSDD público: `python scripts/bsdd_client.py --help`.
- IDS: IfcTester/IfcOpenShell com versões fixadas pelo projeto.
- IFC: IfcOpenShell e documentação do schema correspondente.
- Runtime obrigatório: executar `python scripts/verify_ifc_runtime.py` antes de inventário, relações, mapeamento pós-exportação ou IDS; bloquear quando `safe_to_execute` não for `true` e registrar as versões no relatório.
- Mapeamento pré/pós-exportação: `python scripts/ifc_mapping_validator.py --help`; exigir matriz JSON conforme `references/ifc-mapping-rules.schema.json`.
- Mapeamentos Revit/IFC e COBie: `python scripts/parameter_mappings.py --help`. Consultar `references/parameter-mappings.md`; nunca carregar o mapeamento IFC-SG.
- BCF: implementação BCF-XML ou BCF API declarada pelo projeto.
- Ingresso de privacidade: `python scripts/privacy_ingest.py <arquivo> --cleared-root data/input/cleared`; compartilhar somente o JSON seguro produzido.
- Verificação local: `python scripts/privacy_gate.py <arquivo-opaco> --root data/input/cleared`.
- Instalação/reconstrução: `python scripts/install_ifc_runtime.py`; depois recriar os sandboxes existentes do OpenClaw para adotar `openclaw-sandbox-ifc:0.8.5`.

Se a ferramenta necessária não estiver disponível, retornar `warning`, explicar a lacuna e fornecer um próximo passo verificável.
