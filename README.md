# Information Manager IFC Skill

## Runtime IFC/IDS fixado

Construa e valide a imagem determinística:

```powershell
python scripts/install_ifc_runtime.py
```

A configuração fixa `openclaw-sandbox-ifc:0.8.5`, contendo `ifcopenshell==0.8.5` e `ifctester==0.8.5`. Depois de aplicar a configuração ao OpenClaw, execute `openclaw sandbox recreate --all`.

Valide a execução real de IFC e IDS, sem rede:

```powershell
docker run --rm --network none `
  -v "${PWD}:/skill:ro" -w /skill `
  openclaw-sandbox-ifc:0.8.5 `
  python scripts/smoke_ifc_ids_runtime.py
```

O teste cria um IFC temporário dentro do container e exige dois elementos
aplicáveis: um aprovado e um reprovado. Resultado `0/0` bloqueia a aceitação.

## Compatibilidade Claude Code

O repositório inclui `CLAUDE.md`, a skill em `.claude/skills/information-manager-ifc/` e agentes em `.claude/agents/`. Abra o Claude Code na raiz e use `claude --agent ifc-coordinator`. OpenClaw e Claude compartilham os mesmos scripts e referências.

Instale o runtime local isolado do Claude uma vez com `python scripts/install_claude_runtime.py`. Execute scripts aprovados por `python scripts/run_ifc_python.py <script> [argumentos]`; o launcher bloqueia scripts fora da allowlist.

Equipe principal: `ifc-coordinator` (Sebastian), `ifc-inventory`, `ifc-mapping-validator`, `ifc-parameter-planner` e `ifc-consolidator`. Os demais especialistas são opcionais e só entram quando o requisito envolver relações complexas, IDS, bSDD, BCF ou conhecimento aprovado no Notion.

O Claude mantém integração com o Revit por MCP como executor separado. Os agentes produzem o plano e a SMR; ferramentas MCP de escrita só são usadas por Claude depois da aprovação explícita e no escopo autorizado. Consulte [Claude e MCP — execução controlada no Revit](references/revit-mcp-execution.md).

O `revit-mcp-server` pode permanecer ativo com todas as suas ferramentas disponíveis e aprovadas para uso pelo Claude executor. Essa aprovação é de capacidade; cada operação que modifique o modelo continua vinculada à SMR correspondente. Os subagentes de análise não recebem o MCP.

### Restrição para máquina corporativa

O runtime local acima é apenas compatibilidade de desenvolvimento e não autoriza agentes no host corporativo. Em ambiente corporativo, o coordenador e os especialistas Claude também devem estar confinados em containers; colocar apenas os scripts IFC no Docker não cria essa fronteira. O OpenClaw permanece autorizado até o substituto demonstrar isolamento e equivalência determinística conforme [Segurança do runtime de agentes](references/agent-runtime-security.md).

Skill modular para gestão da informação BIM, organizada em cinco conhecimentos especializados:

1. Revit–IFC: configuração, exportação e rastreabilidade por versão.
2. IDS: formalização e validação de requisitos de informação.
3. ISO 19650: requisitos, planos de entrega, CDE e estados da informação.
4. bSDD: pesquisa de dicionários, classes e propriedades por URI estável.
5. BCF: gestão de tópicos, responsáveis, estados e evidências de coordenação.

O arquivo `SKILL.md` funciona como roteador. O conteúdo técnico fica em `references/`, evitando carregar conhecimento que não seja necessário à tarefa.

O hub privado [OpenBIM Knowledge RAG](https://app.notion.com/p/3a4be9ae75ad810b9c17cad02da8db3d) é o catálogo consultivo único dos agentes. Ele contém somente fontes, conceitos e regras técnicas aprovadas; não recebe modelos de projeto, conversas ou resultados. Em cada máquina, configure o MCP oficial do Notion e conclua o OAuth localmente.

```powershell
openclaw mcp add notion --url https://mcp.notion.com/mcp --transport streamable-http --auth oauth --include notion-search,notion-fetch,notion-get-self
openclaw mcp login notion
openclaw mcp doctor notion --probe
```

Use uma instância/processo OpenClaw dedicado ao recuperador e configure nele somente o MCP Notion. O `bundle-mcp` agrega servidores disponíveis; portanto, adicionar MCPs alheios ao mesmo processo quebra o isolamento pretendido. A conta/integração Notion deve ter acesso exclusivo ao hub OpenBIM.

Todo arquivo passa primeiro pelo ingresso local determinístico. Todo IFC/STEP é classificado como sensível e recebe `LOCAL_ONLY`: o processo cria um snapshot byte a byte com nome SHA-256, sem anonimizar ou regravar o conteúdo. Coordenador e workers IFC autorizados podem ler o snapshot dentro do Docker, em volume somente leitura. O arquivo não pode ser transferido ao Notion, bSDD ou serviços externos não aprovados. `REVIEW` e `BLOCK` interrompem o fluxo.

```powershell
python scripts/privacy_ingest.py "C:\origem\modelo.ifc" --sensitive-root data/input/sensitive
```

## Documentação visual e manual

- [Fluxo conceitual dos agentes IFC](docs/FLUXO-CONCEITUAL-AGENTES-IFC.html): mostra IDM, fontes, roteamento, validação, consolidação e decisão humana.
- [Arquitetura OpenClaw dos agentes IFC](docs/ARQUITETURA-OPENCLAW-AGENTES-IFC.html): apresenta camadas, agentes instalados, ferramentas determinísticas e segurança operacional.
- [Manual para criação de regras de mapeamento IFC](docs/MANUAL-CRIACAO-REGRAS-MAPEAMENTO-IFC.docx): orienta a criação da matriz categoria, classe IFC e `PredefinedType`.
- [Manual de RAG Revit→IFC e OpenClaw em VPS](docs/MANUAL-RAG-REVIT-IFC-OPENCLAW-VPS.md): descreve governança no Notion, embeddings controlados, relações determinísticas, segurança e implantação em VPS.

## Validação de mapeamento IFC

O agente `ifc-mapping-validator` executa auditorias pré e pós-exportação. Ele compara o CSV autoral com uma matriz aprovada pelo projeto/IDM e, quando houver IFC e `GlobalId` comum, confirma a classe e o `PredefinedType` efetivamente exportados.

```powershell
python scripts/ifc_mapping_validator.py `
  --source-csv modelo-autoral.csv `
  --rules regras-projeto.json `
  --ifc modelo-exportado.ifc `
  --output resultado.json
```

Templates: `references/ifc-mapping-source-template.csv` e `references/ifc-mapping-rules.template.json`.

## Mapeamentos Revit/IFC e COBie

A skill inclui quatro fontes autorizadas e um parser determinístico para consultar nomes, GUIDs, tipos de dados e escopo de instância/tipo:

```powershell
python scripts/parameter_mappings.py stats
python scripts/parameter_mappings.py query CasingDepth --scope type
```

O mapeamento regional IFC-SG/Singapura não está incluído nem é carregado pelo parser. O Notion cataloga os quatro conjuntos, seus hashes e sua autorização de embeddings; as 10.378 linhas permanecem em snapshots Git consultados pelo parser. Consulte `references/parameter-mappings.md` para proveniência e limites.

## Consulta inicial de parâmetros e destinos IFC

Use `templates/Template_Consulta_Parametros_Revit_IFC.xlsx` para registrar a
entrada do requisito e a saída do planejamento. A saída separa
`ATTRIBUTE`, `STANDARD_QTO`, `CUSTOM_QTO`, `STANDARD_PSET`, `CUSTOM_PSET`,
`MATERIAL_ASSOCIATION`, `CALCULATED_ONLY` e `UNVERIFIED`; o campo combinado
`Pset_ou_Qto` não faz parte do contrato.

Consulte [Destino técnico da informação no IFC](references/ifc-information-destination.md).
Um `CUSTOM_QTO` só é aprovado no Gate 4 quando o IFC exportado comprova
`IfcElementQuantity` e o subtipo `IfcQuantity*` esperado.

Para definir presença opcional, obrigatória e multiplicidade dos valores,
consulte o [Guia técnico de cardinalidade em requisitos BIM e IDS](docs/guias/Guia_Cardinalidade_Requisitos_IDS.md).

## Liberação

O primeiro uso deve ocorrer como produção assistida. Os critérios para
entrada, homologação e versionamento de correções estão em
[Checklist de produção assistida](references/production-assisted-checklist.md).

## Consulta bSDD

O cliente `scripts/bsdd_client.py` implementa operações públicas e somente leitura da API oficial, sem dependências externas:

```powershell
python scripts/bsdd_client.py dictionaries --limit 5
python scripts/bsdd_client.py search-classes parede --dictionary-uri "URI_DO_DICIONARIO"
python scripts/bsdd_client.py class "URI_DA_CLASSE" --language pt-BR
python scripts/bsdd_client.py class-properties "URI_DA_CLASSE"
python scripts/bsdd_client.py property "URI_DA_PROPRIEDADE"
python scripts/bsdd_client.py text-search fire --type-filter Property
```

A saída é JSON estruturada, apropriada para scripts e nós Execute Command/Code do n8n. Ela registra URL consultada, contrato e instante UTC; os dados permanecem dinâmicos. Resultados da API são evidência técnica, enquanto decisões de conformidade continuam exigindo o requisito contratual e aprovação humana.

## OpenClaw

Instale a pasta completa como skill gerenciada:

```powershell
Copy-Item -LiteralPath . -Destination "$HOME/.openclaw/skills/information-manager-ifc" -Recurse
```

Substitua `__SKILL_ROOT__` nos arquivos de exemplo pelo caminho absoluto da skill e incorpore a configuração ao `~/.openclaw/openclaw.json`. O exemplo usa sandbox Docker, workspaces somente leitura, profundidade 1 e allowlist explícita de agentes. Acesso de rede é liberado apenas para `bsdd-researcher`.

## Testes

```powershell
python -m unittest discover -s tests -v
```

Contrato usado: [buildingSMART Dictionaries API v1](https://app.swaggerhub.com/apis/buildingSMART/Dictionaries/v1). Base de produção: `https://api.bsdd.buildingsmart.org`.

## Licença

O código e a documentação autoral deste repositório usam [MIT](LICENSE). Os quatro TXT em `references/parameter-mappings/sources/` vêm do projeto Autodesk Revit IFC e permanecem sob LGPLv2; consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
