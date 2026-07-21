# Information Manager IFC Skill

Skill modular para gestão da informação BIM, organizada em cinco conhecimentos especializados:

1. Revit–IFC: configuração, exportação e rastreabilidade por versão.
2. IDS: formalização e validação de requisitos de informação.
3. ISO 19650: requisitos, planos de entrega, CDE e estados da informação.
4. bSDD: pesquisa de dicionários, classes e propriedades por URI estável.
5. BCF: gestão de tópicos, responsáveis, estados e evidências de coordenação.

O arquivo `SKILL.md` funciona como roteador. O conteúdo técnico fica em `references/`, evitando carregar conhecimento que não seja necessário à tarefa.

## Documentação visual e manual

- [Fluxo conceitual dos agentes IFC](docs/FLUXO-CONCEITUAL-AGENTES-IFC.html): mostra IDM, fontes, roteamento, validação, consolidação e decisão humana.
- [Arquitetura OpenClaw dos agentes IFC](docs/ARQUITETURA-OPENCLAW-AGENTES-IFC.html): apresenta camadas, agentes instalados, ferramentas determinísticas e segurança operacional.
- [Manual para criação de regras de mapeamento IFC](docs/MANUAL-CRIACAO-REGRAS-MAPEAMENTO-IFC.docx): orienta a criação da matriz categoria, classe IFC e `PredefinedType`.

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

O mapeamento regional IFC-SG/Singapura não está incluído nem é carregado pelo parser. Consulte `references/parameter-mappings.md` para proveniência, hashes e limites de interpretação.

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
