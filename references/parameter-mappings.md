# Mapeamentos de parâmetros Revit/IFC e COBie

## Finalidade

Usar esta base para verificar nomes, GUIDs, tipos de dados e escopo de parâmetros antes de interpretar uma ausência no IFC. Tratar os resultados como evidência de configuração/exportação Revit, não como definição normativa universal do schema IFC.

## Consulta determinística

Executar pela raiz da skill:

```bash
python scripts/parameter_mappings.py stats
python scripts/parameter_mappings.py query CasingDepth --scope instance
python scripts/parameter_mappings.py query FireRating --source-kind revit-shared
python scripts/parameter_mappings.py query COBie.Type.NominalLength --source-kind cobie-ifc2x3
```

Filtros disponíveis:

- `--scope instance|type|unspecified`
- `--source-kind revit-shared|user-defined-pset|cobie-ifc2x3`
- `--limit N`

O resultado JSON fornece `source_file` e `source_line`. Registrar ambos na evidência.

O catálogo Notion `Conjuntos de Mapeamentos Revit IFC` controla aprovação, hash e autorização de embeddings. Antes de usar uma relação na decisão, exigir conjunto `Aprovado`, conferir o SHA-256 e manter o escopo `instance` ou `type`.

## Fontes autorizadas

| Fonte | Uso | SHA-256 |
|---|---|---|
| `IFC Shared Parameters-RevitIFCBuiltIn_ALL.txt` | Parâmetros de ocorrência/instância | `D5317EACB84D8BF25DD6EEBD6E1D0E72D3317BD4D17DE281E89C782BFC07EAA7` |
| `IFC Shared Parameters-RevitIFCBuiltIn-Type_ALL.txt` | Parâmetros de tipo | `3DD321590A24E75DB10B7CB52F847093D6904F8596CB2E8F13C98A7ABAEF6928` |
| `DefaultUserDefinedParameterSets.txt` | Sintaxe e tipos aceitos para Psets personalizados; atualmente contém modelo/comentários, sem registros ativos | `20297D13B1E39275390180E71538DF6623966F57E24C200C738E2964E3386369` |
| `IFC2x3 COBie 2.4 Design Deliverable.txt` | Mapeamento COBie 2.4 associado a IFC2x3 | `894978EFB39D978AABCBBD04084FA19C09D59A9AD2D5539306EF9A46A58B024E` |

Os originais preservados ficam em `references/parameter-mappings/sources/`.

## Exclusão obrigatória

Não carregar, consultar, copiar ou inferir regras a partir de `IFC-SG Property Mapping Export.txt`. Esse material é regional de Singapura e foi excluído por decisão do proprietário da skill. O parser usa uma allowlist fixa de quatro arquivos e não faz descoberta automática de TXT.

## Interpretação

Aplicar esta ordem:

1. Confirmar versão do Revit, exportador e schema IFC do projeto.
2. Consultar nome exato, GUID, escopo e tipo de dado nesta base.
3. Inspecionar o IFC exportado com ferramenta determinística.
4. Classificar o achado:
   - parâmetro não encontrado na base;
   - mapeamento conhecido, valor ausente no modelo de autoria;
   - valor presente no Revit, mas não exportado;
   - instância/tipo incompatível;
   - tipo de dado incompatível;
   - não verificável com as evidências disponíveis.
5. Consultar schema IFC, IDS ou bSDD quando a conclusão exigir significado normativo.

O encadeamento de evidência deve ser: `categoria Revit → parâmetro/export setting → candidato de classe/Pset/propriedade → schema IFC aplicável → requisito IDS/IDM → resultado exportado`. Uma correspondência do TXT gera candidato; somente regra executável e inspeção do IFC produzem aprovação ou falha.

Não concluir que um parâmetro é obrigatório apenas porque aparece nesta base. Não generalizar o arquivo COBie para IFC4/IFC4.3. Não tratar correspondência textual como equivalência semântica confirmada.

## Uso pelos agentes

- `ifc-inventory`: medir cobertura dos Psets e separar instância de tipo.
- `ifc-class-worker`: verificar propriedade, GUID, tipo Revit/IFC e linha da fonte.
- `ids-validator`: usar o mapeamento para preparar candidatos a requisitos, nunca para inventar obrigatoriedade.
- `bsdd-researcher`: confirmar semântica e URI quando houver correspondência possível.
- `bcf-coordinator`: citar evidência de mapeamento ao registrar falha de exportação.
- `ifc-consolidator`: separar erro de autoria, configuração de exportação e não verificado.
