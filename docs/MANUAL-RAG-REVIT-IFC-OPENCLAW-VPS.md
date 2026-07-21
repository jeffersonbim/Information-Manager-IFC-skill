# Manual — RAG Revit→IFC, Notion e OpenClaw em VPS

## Objetivo

Este manual descreve como relacionar os mapeamentos da pasta `revit` ao conhecimento IFC, como governar essas relações no Notion e como operar a skill `information-manager-ifc` em uma VPS sem permitir que a IA transforme hipóteses em regras aprovadas.

## O que foi incorporado

Foram catalogados no Notion quatro conjuntos autorizados:

| Conjunto | Escopo | Registros |
|---|---|---:|
| Shared Parameters Revit IFC | Instância | 5.211 |
| Shared Parameters Revit IFC | Tipo | 5.130 |
| User Defined Property Sets | Template, sem regras ativas | 0 |
| COBie 2.4 Design Deliverable | IFC2X3, instância e tipo | 37 |

Total: **10.378 relações normalizadas**. O arquivo `IFC-SG Property Mapping Export.txt` permanece excluído por decisão anterior e não é descoberto automaticamente pelo parser.

Os registros do Notion foram criados como **Em revisão** e com **Embeddings autorizados = não**. A versão do exportador Revit não está declarada nos principais arquivos; aprová-los sem identificar a versão criaria falsa precisão.

## Como o agente relaciona a informação

```text
Categoria Revit
  → parâmetro e configuração de exportação
  → candidato IfcClass / PredefinedType
  → candidato Pset / propriedade
  → schema IFC da entrega
  → regra IDS ou requisito IDM
  → inspeção do IFC exportado
  → PASS / FAIL / NÃO VERIFICÁVEL
```

O TXT produz candidatos de mapeamento. A conclusão depende da versão do Revit/exportador, do schema, da regra aprovada e do objeto realmente exportado.

### Consulta determinística

Na raiz da skill:

```powershell
python scripts/parameter_mappings.py stats
python scripts/parameter_mappings.py query FireRating --scope instance
python scripts/parameter_mappings.py query CasingDepth --scope type
python scripts/parameter_mappings.py query COBie.Type.NominalLength --source-kind cobie-ifc2x3
```

Registrar sempre `source_file`, `source_line`, `scope`, hash do conjunto e schema.

## Função do Notion

O Notion é o catálogo editorial e consultivo:

- identifica a fonte e sua versão;
- mantém status `Rascunho`, `Em revisão`, `Aprovado` ou `Obsoleto`;
- registra o SHA-256 do snapshot;
- autoriza ou bloqueia embeddings;
- relaciona fonte, conceito, regra, IDS e IDM.

O Notion não substitui o snapshot Git nem o validador. Milhares de linhas são consultadas pelo parser/índice; o Notion controla se aquele conjunto pode ser usado.

## RAG avançado com embeddings controlados

1. O sincronizador lê somente registros `Aprovado` e `Embeddings autorizados = sim`.
2. Compara o SHA-256 do Notion com o arquivo no Git.
3. Normaliza cada relação em um documento pequeno e acrescenta metadados.
4. Gera embeddings com modelo e versão fixos.
5. Grava em pgvector ou Qdrant.
6. A busca combina palavra exata, vetor e filtros de schema, classe, escopo e versão.
7. O agente recupera candidatos; o validador determinístico decide conformidade.

Metadados mínimos:

```json
{
  "mapping_set": "MAP-REVIT-IFC-INST-001",
  "source_hash": "sha256",
  "revit_scope": "instance",
  "revit_parameter": "FireRating",
  "ifc_pset": "Pset_...",
  "ifc_property": "...",
  "schema": "IFC4",
  "status": "Aprovado",
  "embedding_model": "modelo@versão"
}
```

## Arquitetura da VPS

```text
Usuário / canal privado
       ↓
OpenClaw Orchestrator
       ├─ Privacy Gate
       ├─ Recuperador Notion com ferramentas filtradas para leitura
       ├─ Busca híbrida no índice vetorial
       ├─ Parser Revit→IFC
       ├─ Validador IFC/IDS
       └─ Consolidador + revisão humana

Notion → sincronizador → pgvector/Qdrant
Git → snapshots/regras → parser/validador
```

Separar em serviços/contêineres:

- gateway OpenClaw;
- recuperador Notion;
- sincronizador;
- PostgreSQL + pgvector ou Qdrant;
- workers IFC sem acesso de escrita ao Notion;
- armazenamento de entrada temporário e criptografado.

### Segurança mínima

- HTTPS e firewall; não expor o gateway diretamente sem autenticação;
- MCP Notion com apenas `search`, `fetch` e identificação da conexão;
- usuário OAuth dedicado, MFA e acesso exclusivo ao hub OpenBIM;
- reconhecer que o OAuth herda as permissões do usuário: o bloqueio de escrita é implementado pelo filtro do OpenClaw e pelo Gateway dedicado, não por uma credencial Notion read-only;
- nenhum modelo IFC, conversa ou resultado de projeto no Notion;
- segredos fora do Git;
- disco criptografado, backup e rotação de logs;
- acesso aos arquivos por caminho opaco após o Privacy Gate;
- redação, retenção curta e limpeza de sessões/logs, pois tool calls podem persistir nos transcritos do OpenClaw;
- retenção e exclusão definidas para arquivos temporários;
- agentes não aprovam regras nem publicam alterações.

## Relações novas geradas pelos agentes

Os agentes podem sugerir novas relações, mas devem gravá-las apenas como proposta ou arquivo de revisão contendo:

- hipótese normalizada;
- evidências e linhas das fontes;
- schema e versões;
- objeto IFC de teste anonimizado ou resultado agregado;
- nível de confiança;
- conflitos encontrados;
- teste determinístico proposto.

Fluxo de promoção:

```text
PROPOSTA → teste → revisão BIM → aprovação → regra versionada → reindexação
```

Não implementar `agente → Aprovado` automaticamente. Repetição de uma relação não a transforma em verdade.

## A classificação ficará mais precisa?

Provavelmente sim, porque a skill reduzirá candidatos usando categoria, escopo, schema, versão e evidência pós-exportação. O benefício é maior para consultas repetitivas e padronizadas.

Porém, a precisão só é mensurável com um conjunto de teste. Criar casos conhecidos para `IfcWall`, `IfcDoor`, `IfcSlab` e equipamentos; medir classe correta, `PredefinedType`, Psets, falsos positivos, falsos negativos e respostas `NÃO VERIFICÁVEL`.

Uma meta inicial realista é melhorar a precisão top-1 sem reduzir artificialmente os casos de dúvida. O agente deve preferir `NÃO VERIFICÁVEL` a uma classificação sem evidência.

## Checklist de ativação

- [ ] Identificar versão de cada arquivo/exportador Revit.
- [ ] Revisar os quatro conjuntos no Notion.
- [ ] Aprovar somente conjuntos testados.
- [ ] Autorizar embeddings separadamente.
- [ ] Configurar usuário OAuth dedicado ao hub, MFA, auditoria e filtro estrito das três ferramentas de leitura.
- [ ] Configurar redação, retenção e limpeza dos transcritos OpenClaw.
- [ ] Subir pgvector/Qdrant e sincronizador.
- [ ] Fixar modelo de embedding e versão.
- [ ] Executar casos de teste conhecidos.
- [ ] Manter revisão humana antes de promover novas relações.
- [ ] Monitorar precisão e lacunas por schema e categoria.
