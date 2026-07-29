# Planejamento conceitual de informações Revit–IFC

## Objetivo

Transformar cada necessidade em uma decisão única para autoria BIM e
intercâmbio IFC. Responder na tela; não criar arquivos, GUIDs ou artefatos nesse
fluxo, salvo solicitação explícita posterior.

## Princípios

1. Classificar o elemento pela função real.
2. Usar categoria Revit específica, escrita em inglês.
3. Trabalhar somente no schema IFC solicitado.
4. Priorizar conteúdo padronizado antes de propor conteúdo customizado.
5. Não duplicar a mesma informação em destinos diferentes.
6. Apresentar uma única decisão por campo.
7. Não usar `Generic Models`.

## Ordem da análise

Para cada necessidade:

1. identificar a disciplina responsável;
2. definir uma categoria Revit;
3. definir uma classe IFC compatível com a função;
4. verificar se a informação é nativa;
5. verificar se existe definição reutilizável;
6. classificar a situação como `NATIVE`, `REUSE` ou `CUSTOM`;
7. definir exatamente um parâmetro;
8. definir o escopo como `Instância` ou `Tipo`;
9. definir exatamente um destino IFC;
10. definir tipo de dado e unidade;
11. apresentar uma recomendação executável.

## Prioridade do destino IFC

Pesquisar nesta ordem:

1. atributo;
2. quantidade oficial;
3. propriedade oficial;
4. associação de material;
5. relação com sistema, classificação ou outro objeto;
6. propriedade customizada.

Nunca responder `Pset ou Qto`.

## Regras conceituais

- Tratar altura, largura, comprimento, espessura, diâmetro, área e volume como
  dados geométricos básicos.
- Direcionar grandezas mensuráveis a quantidades IFC quando houver definição
  aplicável no schema.
- Representar o material real por associação de material.
- Usar texto para descrição, classificação ou composição, não para substituir
  material ou quantidade.
- Relacionar elementos MEP ao sistema técnico quando essa relação estiver
  disponível.
- Separar fase do projeto de faseamento construtivo.
- Usar `Tipo` para valores comuns às ocorrências e `Instância` para valores que
  podem variar individualmente.
- Usar texto controlado para enumerações e uma grafia única por valor.
- Não sugerir um novo nome quando uma definição existente for semanticamente e
  tecnicamente compatível.

## Formato obrigatório de saída

Separar a resposta por categoria. Usar uma tabela por categoria:

| Necessidade | Disciplina | Categoria Revit | Classe IFC | Situação | Parâmetro Revit | Escopo | Destino IFC | Tipo de dado | Unidade de medida | Recomendação |
|---|---|---|---|---|---|---|---|---|---|---|
| Informação solicitada | Disciplina responsável | Categoria em inglês | Classe do schema | `NATIVE`, `REUSE` ou `CUSTOM` | Nome único | `Instância` ou `Tipo` | Destino único | Tipo coerente | Unidade ou `Sem unidade` | Ação única |

## Regras da tabela

- Não incluir alternativas na mesma célula.
- Usar o nome nativo exato quando a situação for `NATIVE`.
- Sugerir um único nome normalizado quando a situação for `CUSTOM`.
- Informar o caminho exato do destino IFC.
- Declarar a unidade separadamente do nome do parâmetro.
- Usar uma recomendação curta e executável.

## Exemplo

| Necessidade | Disciplina | Categoria Revit | Classe IFC | Situação | Parâmetro Revit | Escopo | Destino IFC | Tipo de dado | Unidade de medida | Recomendação |
|---|---|---|---|---|---|---|---|---|---|---|
| Comprimento | Disciplina responsável | `Categoria específica` | `IfcClasseAplicável` | `NATIVE` | `Length` | Instância | `BaseQuantities.Length` | Comprimento | m | Exportar como Qto |
| Material | Disciplina responsável | `Categoria específica` | `IfcClasseAplicável` | `NATIVE` | `Material` | Tipo | `IfcRelAssociatesMaterial` | Material | Sem unidade | Exportar a associação |
| Classificação | Disciplina responsável | `Categoria específica` | `IfcClasseAplicável` | `CUSTOM` | `ClassificacaoEspecifica` | Tipo | `SUP_Classification.ClassificationType` | Texto controlado | Sem unidade | Preencher com valor aprovado |

## Limite

A proposta é conceitual. Confirmar o resultado em um IFC exportado antes de
declarar atendimento ou conformidade.
