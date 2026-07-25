# Destino técnico da informação no IFC

## Finalidade

Classificar cada requisito de informação sem confundir atributo, quantidade,
propriedade, associação ou cálculo. A classificação sempre depende do schema
IFC exato e deve ser confirmada no IFC realmente exportado.

## Ordem de decisão

1. `ATTRIBUTE`: atributo nativo da entidade.
2. `STANDARD_QTO`: quantidade padronizada aplicável ao schema.
3. `STANDARD_PSET`: propriedade de Pset oficial.
4. `MATERIAL_ASSOCIATION`: associação IFC de material.
5. `CUSTOM_QTO`: quantidade física customizada.
6. `CUSTOM_PSET`: informação descritiva customizada.
7. `CALCULATED_ONLY`: cálculo que não precisa ser entregue no IFC.
8. `UNVERIFIED`: evidência insuficiente.

A ordem é uma prioridade de reuso e interoperabilidade, não uma autorização
para inventar obrigatoriedade.

## Regra para Qto customizado

Usar `CUSTOM_QTO` somente quando o requisito representar grandeza física
mensurável e estiverem definidos:

- `QuantitySet`;
- `QuantityName`;
- `QuantityType`, como `IfcQuantityLength`, `IfcQuantityArea`,
  `IfcQuantityVolume`, `IfcQuantityCount`, `IfcQuantityWeight` ou
  `IfcQuantityTime`;
- unidade;
- `MethodOfMeasurement`;
- fórmula ou origem geométrica;
- nível de ocorrência ou tipo;
- classes IFC aplicáveis.

O Gate 4 somente aprova o mapeamento quando a inspeção do IFC comprovar
`IfcElementQuantity` e o subtipo `IfcQuantity*` esperado. Se o exportador
produzir `IfcPropertySet` e `IfcPropertySingleValue`, classificar como Pset,
independentemente do nome utilizado no Revit.

## Compatibilidade de schema

Não transportar automaticamente nomes de templates
`Qto_*BaseQuantities` entre IFC2X3, IFC4 e IFC4.3. Em IFC2X3,
`IfcElementQuantity` admite conjuntos de quantidades e métodos de medição, mas
o nome e o conteúdo adotados pelo projeto/exportador precisam de evidência no
schema e no arquivo exportado. Em IFC4/IFC4.3, usar somente Quantity Set
Templates aplicáveis à versão declarada.

## Exemplo: porta com bandeira

| Informação | Destino inicial recomendado | Condição |
|---|---|---|
| Largura total | `ATTRIBUTE` | `IfcDoor.OverallWidth`, quando aplicável |
| Altura total | `ATTRIBUTE` | `IfcDoor.OverallHeight`, quando aplicável |
| Possui bandeira | `CUSTOM_PSET` | booleano descritivo |
| Largura da bandeira | `CUSTOM_QTO` ou `CUSTOM_PSET` | Qto somente se for medição contratual e o exportador comprovar a entidade |
| Altura da bandeira | `CUSTOM_QTO` ou `CUSTOM_PSET` | mesma regra |
| Área da bandeira | `CALCULATED_ONLY` ou `CUSTOM_QTO` | documentar fórmula e método de medição |
| Material da bandeira | `MATERIAL_ASSOCIATION` ou Pset | associação quando representar o material efetivo |

## Campos mínimos do template

- identificação: código, descrição, disciplina, fase e requisito de origem;
- aplicabilidade: categoria Revit, classe IFC e `PredefinedType`;
- autoria: parâmetro Revit, nativo/customizado, instância/tipo, datatype, GUID;
- destino: `Destino_IFC_Tipo`, atributo, Quantity Set/Name/Type,
  `MethodOfMeasurement`, fórmula, Pset, propriedade, datatype IFC e associação;
- comprovação: versão do Revit/exportador, schema, entidade exportada, evidência,
  status do gate e decisão humana.

## Fontes primárias

- buildingSMART, IFC2x3 TC1: `IfcElementQuantity`.
- buildingSMART, IFC2x3 TC1: `IfcDoor`.
- buildingSMART, IFC4.3: Quantity Sets e Quantity Set Templates.

As referências normativas completas devem ser registradas no artigo e no
registro de decisão do projeto.
