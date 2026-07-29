---
name: information-manager-ifc
description: Orquestra análise IFC no OpenClaw com RAG técnico OpenBIM no Notion, preflight local LGPD e agentes isolados para inventário, classes, relações, mapeamento de exportação, IDS, bSDD, BCF e consolidação, além de orientar Revit-IFC e ISO 19650. Usar ao consultar conhecimento aprovado, inspecionar IFC, validar categoria autoral contra classe IFC e PredefinedType, verificar requisitos, pesquisar conceitos buildingSMART, produzir cobertura ou registrar não conformidades. Exigir Notion como catálogo consultivo único, minimização, evidência determinística e revisão humana antes de transmitir conteúdo, alterar modelos, publicar dados ou declarar conformidade.
---

# Information Manager IFC

Atuar como roteador e orquestrador OpenClaw. Carregar somente o conhecimento necessário à solicitação.

## Orquestração OpenClaw

Para analisar um IFC completo, ler `references/agent-orchestrator.md` e executar este fluxo:

1. Exigir ingresso local com `scripts/privacy_ingest.py` antes de enviar qualquer nome, caminho ou conteúdo ao OpenClaw.
2. Acionar `privacy-gate` somente com o manifesto seguro, o caminho opaco `/dados-ifc/sensitive/<hash>.<ifc|step>` para IFC/STEP e o objetivo.
3. Para IFC/STEP, exigir `LOCAL_ONLY` e permitir que coordenador e workers autorizados leiam o snapshot íntegro somente dentro do Docker isolado e somente leitura. Para outros formatos, prosseguir em `ALLOW`; interromper em `REVIEW` ou `BLOCK`.
4. Acionar `openbim-knowledge-retriever` para recuperar conceitos, regras e conjuntos Revit→IFC aprovados aplicáveis ao schema.
5. Acionar `ifc-inventory` para identificar schema, unidades, classes, Psets e população em saída minimizada.
6. Acionar `ifc-mapping-validator` para relacionar categoria autoral, classe IFC, `PredefinedType` e resultado exportado.
7. Acionar `ifc-parameter-planner` para classificar parâmetros nativos, configurações, cálculos, parâmetros a criar, conflitos e lacunas.
8. Acionar `ifc-consolidator` para reconciliar evidências e produzir o plano final; criar SMR quando houver mudança no Revit.
9. Acionar relações, IDS, bSDD, BCF ou recuperador de conhecimento somente quando o objetivo exigir.
10. Criar lotes temporários por classe apenas quando o volume exigir; não criar agentes permanentes adicionais.
11. Manter o isolamento padrão de sessão do `sessions_spawn` e enviar tarefas autocontidas. Usar `sessions_yield` após os spawns; não fazer polling.

Perfis e contratos:

- `references/agent-orchestrator.md`
- `references/agent-privacy-gate.md`
- `references/agent-openbim-knowledge-retriever.md`
- `references/agent-inventory.md`
- `references/agent-class-worker.md`
- `references/agent-mapping-validator.md`
- `references/agent-parameter-planner.md`
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
| Relacionar e classificar parâmetros para criação/reuso | `references/agent-parameter-planner.md` + `references/parameter-mappings.md`; produzir plano e SMR, nunca alterar o Revit |
| Planejar necessidades por disciplina, revisar parâmetros compartilhados ou gerar os quatro artefatos de entrega | `references/parameter-planning-workflow.md` + `references/agent-parameter-planner.md` |
| Distinguir atributo, Qto, Pset, cálculo ou material | `references/ifc-information-destination.md` + `references/agent-parameter-planner.md`; exigir schema exato e evidência do IFC exportado |
| Executar no Revit via Claude/MCP | `references/revit-mcp-execution.md`; leitura antes da aprovação e escrita limitada à SMR aprovada |
| Criar, revisar ou executar `.ids` | `references/ids.md` |
| OIR, AIR, PIR, requisitos de troca, BEP, TIDP, MIDP, CDE, PIM ou AIM | `references/iso19650.md` |
| Pesquisar dicionários, classes, propriedades, URIs ou valores permitidos | `references/bsdd.md` |
| Criar, atribuir, acompanhar ou encerrar issues de coordenação | `references/bcf.md` |
| Instalar, verificar ou relatar o executor IFC/IDS | `references/ifc-runtime.md` + `scripts/install_ifc_runtime.py` + `scripts/verify_ifc_runtime.py` |
| Executar ou migrar agentes em máquina corporativa | `references/agent-runtime-security.md`; bloquear runtime no host e exigir equivalência de isolamento antes de substituir o OpenClaw |

Carregar mais de um conhecimento quando a tarefa atravessar domínios. Exemplos:

- Transformar requisito contratual em IDS: ISO 19650 + IDS.
- Mapear propriedade no Revit usando conceito oficial: Revit-IFC + bSDD.
- Reportar falha IDS como issue: IDS + BCF.

## Fluxo obrigatório

1. **Gatilho de template:** quando uma planilha `.xlsx` compatível com `Template_Consulta_Parametros_Revit_IFC.xlsx` for anexada na conversa, iniciar automaticamente a triagem do Gate 1, sem aguardar outro comando: executar `python scripts/template_intake.py <arquivo.xlsx>`, identificar a aba `Entrada_Requisitos`, validar cabeçalhos e separar linhas válidas, incompletas e vazias. Acionar `openbim-knowledge-retriever` e `ifc-parameter-planner` para cada linha válida (em lotes quando necessário) e devolver a proposta de `Saida_Mapeamento`. Não criar, editar, exportar ou aprovar artefatos sem autorização humana.
2. Antes de cada gate técnico, ler `references/gates-questionnaire.md`, apresentar ao usuário a pergunta de decisão e as cinco perguntas orientadoras do gate atual, registrar as respostas pelo identificador e validar a completude com `scripts/gate_questionnaire.py`. A triagem automática do template pode identificar bloqueios e candidatos, mas não avança um gate em estado `BLOCKED`.
3. Tratar todo IFC/STEP como dado sensível e executar o ingresso LGPD fora do LLM; não enviar ao modelo nome, caminho ou conteúdo original.
4. Preservar o IFC byte a byte sob SHA-256. Exigir `LOCAL_ONLY`, montar somente para leitura e permitir acesso ao coordenador e workers IFC autorizados dentro do Docker; conferir o hash antes e depois.
5. Identificar entregável, schema IFC e versões das ferramentas.
6. Declarar premissas quando faltarem dados; não inventar requisitos.
7. Consultar o RAG Notion, aceitar somente registros aprovados e citar a fonte primária; interromper em `KNOWLEDGE_GAP` quando a resposta depender desse conhecimento.
8. Para Revit→IFC, conferir aprovação e hash no Notion, consultar `parameter_mappings.py` e validar o IFC exportado; executar validações determinísticas antes da interpretação por IA.
9. Classificar separadamente origem Revit e destino IFC; nunca usar
   `Pset_ou_Qto`. Um `CUSTOM_QTO` só passa após comprovação de
   `IfcElementQuantity` + `IfcQuantity*` no arquivo exportado.
10. Separar `fato`, `inferência`, `recomendação` e `limitação`.
11. Encaminhar exceções de privacidade, alterações, publicação e declarações formais para aprovação humana.

## Planejamento simplificado de parâmetros

Quando o usuário fornecer uma lista de necessidades:

1. Ler `references/parameter-planning-workflow.md`.
2. Analisar e responder primeiro na tela, usando uma única sugestão por campo.
3. Trabalhar no schema solicitado; se declarado IFC2x3, não transportar classes,
   enumerações, Psets ou Qto exclusivos de IFC4/IFC4.3.
4. Usar categorias Revit em inglês e nunca classificar objetos como
   `Generic Models`.
5. Priorizar atributos, Qto, Psets oficiais e associações de material antes de
   propor parâmetro ou Pset customizado.
6. Revisar o arquivo completo de parâmetros compartilhados ao final de cada
   disciplina, sem editá-lo sem autorização.
7. Gerar os quatro artefatos por disciplina ao final da disciplina e novamente
   ao encerrar a sessão.

### Consulta normativa antes de sugerir criação

Antes de sugerir `PARAMETRO_COMPARTILHADO`, `CUSTOM_PSET` ou `CUSTOM_QTO`,
o agente deve consultar no Notion registros **Aprovados** das fontes ISO
16739-1, ISO 23386 e, quando aplicável, ISO 12006-3. A pergunta deve cobrir
o schema, classe IFC, tipo/ocorrência, conceito, datatype e unidade. A proposta
deve citar a página Notion e a cláusula/seção recuperada, além de registrar a
busca por alternativa padronizada.

Quando essas normas ainda não estiverem disponíveis no Notion, ativar
`BASE_TECNICA_A_CONFIRMAR`: usar os princípios consolidados na skill e a
documentação pública oficial buildingSMART para pesquisar a alternativa IFC,
sem declarar conformidade ISO. A proposta deve trazer URL pública, fato,
inferência, recomendação e limitação. A ausência do PDF não bloqueia a pesquisa
nem a proposta, mas bloqueia aprovação normativa, criação definitiva de GUID e
geração final dos artefatos do Gate 3 até a decisão humana.

### Geração de artefatos no Gate 3

Após a decisão humana explícita por linha (`Aprovacao_Gate_3=APROVADO`), o
coordenador deve gravar a matriz aprovada em JSON e executar
`python scripts/gate3_artifacts.py matriz_aprovada.json --output output/gate3`.
O gerador cria: TXT de Shared Parameters em UTF-16 LE com BOM, manifesto XML
para conferência no Shared Parameters Tool, TXT de Psets customizados no formato
do exportador IFC Autodesk, checkset XML do Model Checker e plano JSON de
evidência para Bonsai/IfcOpenShell. Sem aprovação explícita ou GUID válido em
parâmetro compartilhado, a linha não é gerada. O pacote prepara o Gate 4; não
comprova nem altera o modelo.

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
- Não duplicar atributo IFC nativo em Pset customizado sem requisito e
  justificativa aprovados.
- Não tratar um `IfcPropertySingleValue` como quantidade apenas porque o nome
  contém `Qto`.
- Não reutilizar automaticamente nomes de Quantity Sets entre schemas IFC.
- Não abrir nem encaminhar arquivo antes do `privacy-gate`; `REVIEW` e `BLOCK` interrompem o fluxo.
- Não incluir valores pessoais, trechos detectados ou nomes em prompts, logs ou relatórios do gate.
- Não usar TXT, Markdown local, memória do modelo ou web como base consultiva silenciosa; o Notion é o catálogo consultivo único.
- Não gravar perguntas, conversas, respostas, IFC de projeto ou resultados no hub Notion.
- Não anonimizar, reserializar, normalizar nem regravar o IFC sensível. Preservar o original e o snapshot byte a byte, verificando SHA-256 antes e depois.
- Não transformar `LOCAL_ONLY` em autorização de transferência externa. Agentes autorizados podem ler o IFC dentro do Docker, mas não podem enviar o arquivo ao Notion, bSDD ou APIs alheias ao runtime aprovado.
- Não permitir que workers usem o MCP Revit. Reservar o MCP ao Claude executor e condicionar qualquer escrita à SMR aprovada conforme `references/revit-mcp-execution.md`.
- Não executar agentes IFC diretamente no host corporativo. Colocar somente as ferramentas determinísticas no Docker não atende ao isolamento; aplicar `references/agent-runtime-security.md`.
- Não remover o OpenClaw antes de o runtime substituto passar pelos testes negativos, pela comparação determinística e pela aprovação humana documentada.

## Ferramentas determinísticas

- bSDD público: `python scripts/bsdd_client.py --help`.
- IDS: IfcTester/IfcOpenShell com versões fixadas pelo projeto.
- IFC: IfcOpenShell e documentação do schema correspondente.
- Runtime obrigatório: executar `python scripts/verify_ifc_runtime.py` antes de inventário, relações, mapeamento pós-exportação ou IDS; bloquear quando `safe_to_execute` não for `true` e registrar as versões no relatório.
- Aceitação do runtime: executar `scripts/smoke_ifc_ids_runtime.py` dentro da
  imagem fixada, sem rede e com a skill somente para leitura; exigir um caso
  positivo, um negativo e cobertura diferente de `0/0`.
- Mapeamento pré/pós-exportação: `python scripts/ifc_mapping_validator.py --help`; exigir matriz JSON conforme `references/ifc-mapping-rules.schema.json`.
- Mapeamentos Revit/IFC e COBie: `python scripts/parameter_mappings.py --help`. Consultar `references/parameter-mappings.md`; nunca carregar o mapeamento IFC-SG.
- Questionário dos gates: `python scripts/gate_questionnaire.py questions --gate N`; validar respostas com `python scripts/gate_questionnaire.py validate --gate N resposta.json`.
- Entrada do template: `python scripts/template_intake.py Template_Consulta_Parametros_Revit_IFC.xlsx`; usar a saída JSON como contrato de ingestão, sem inferir colunas ausentes.
- Artefatos Gate 3: `python scripts/gate3_artifacts.py matriz_aprovada.json --output output/gate3`; exige `APROVADO` por linha e GUID controlado para Shared Parameters.
- BCF: implementação BCF-XML ou BCF API declarada pelo projeto.
- Ingresso de privacidade IFC: `python scripts/privacy_ingest.py <arquivo.ifc> --sensitive-root data/input/sensitive`; usar somente o caminho opaco e manter o snapshot íntegro em volume somente leitura.
- Verificação local: `python scripts/privacy_gate.py <arquivo-opaco> --root data/input/cleared`.
- Instalação/reconstrução: `python scripts/install_ifc_runtime.py`; depois recriar os sandboxes existentes do OpenClaw para adotar `openclaw-sandbox-ifc:0.8.5`.

Se a ferramenta necessária não estiver disponível, retornar `warning`, explicar a lacuna e fornecer um próximo passo verificável.
