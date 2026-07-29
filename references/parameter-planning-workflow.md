# Fluxo simples de análise e criação de parâmetros

## Objetivo

Transformar necessidades de informação em uma decisão única e executável para
Revit e IFC2x3, responder primeiro na tela e gerar os artefatos técnicos ao fim
de cada disciplina e de cada sessão.

## Entrada

Receber uma linha por necessidade com, quando disponíveis:

- disciplina;
- descrição do elemento;
- grupo;
- parâmetro solicitado;
- unidade de medida;
- descrição ou exemplo do valor.

Normalizar erros de digitação sem mudar o significado. Preservar códigos,
referências contratuais e nomes aprovados.

## Análise por linha

Executar nesta ordem:

1. Relacionar a disciplina à categoria Revit, escrita em inglês.
2. Relacionar a categoria a uma única classe IFC2x3 aplicável.
3. Verificar se a informação já é nativa no Revit.
4. Verificar se existe destino IFC2x3 padronizado nesta ordem:
   atributo, quantidade oficial, Pset oficial e associação de material.
5. Se for nativo, usar o nome nativo exato e indicar como preencher ou obter o
   valor.
6. Se não for nativo, sugerir um único nome de parâmetro compartilhado, sem
   barras, alternativas ou sinônimos.
7. Definir exatamente um escopo: `Instance` ou `Type`.
8. Definir exatamente um destino IFC.
9. Definir um tipo de dado e uma unidade coerentes com a grandeza.
10. Informar uma única recomendação executável.

Não usar `Generic Models`. Classificar o objeto em sua categoria autoral
específica. Tratar impermeabilização como sistema ou camada associado ao
elemento hospedeiro aplicável, como `Walls`, `Floors` ou `Roofs`.

## Regras de decisão

- Tratar altura, largura, comprimento, espessura, área, volume e diâmetro como
  dados geométricos básicos.
- Encaminhar toda quantidade mensurável que possua template oficial IFC2x3 ao
  `Qto_*BaseQuantities` aplicável.
- Não criar Pset customizado para duplicar atributo, Qto, Pset oficial ou
  associação de material.
- Usar associação IFC de material quando o requisito for o material real do
  elemento. Usar texto customizado somente quando o requisito for uma
  classificação, descrição ou composição não representada pela associação.
- Usar prefixo próprio, como `SUP_`, em Psets customizados. Nunca usar o prefixo
  reservado `Pset_`.
- Usar um único nome sugerido para parâmetro customizado e um único destino.
- Usar `Number` para valores escalares sem unidade, `Boolean` para verdadeiro ou
  falso, `Text` para códigos e enumerações controladas e o tipo físico adequado
  para grandezas.
- Não criar novo GUID se já existir parâmetro compartilhado semanticamente
  equivalente e tecnicamente compatível.
- Detectar e remover duplicidades antes de propor criação.
- Quantidade de louças em paredes significa identificar paredes de áreas
  molhadas; representar essa necessidade por `SUP_AreaMolhada` do tipo
  verdadeiro/falso, e não por uma contagem de louças na parede.

## Formato padrão na tela

Responder em tabela tabulada, sem alternativas em uma mesma célula:

```text
Necessidade	Disciplina	Categoria Revit	Classe IFC2x3	Situação	Parâmetro Revit	Escopo	Destino IFC	Tipo de dado	Unidade de medida	Recomendação
```

Quando o usuário fornecer o formato de origem abaixo, devolver também nesse
formato quando solicitado:

```text
DISCIPLINA	DESCRIÇÃO DO ELEMENTO	GRUPO	[PARÂMETROS]	UNIDADE DE MEDIDA	DESCRIÇÃO DO PARAMÊTRO
```

## Revisão do arquivo de parâmetros compartilhados

Ao finalizar cada disciplina:

1. Ler o arquivo completo autorizado pelo usuário.
2. Comparar nome, GUID, grupo, tipo de dado e descrição.
3. Reutilizar parâmetros compatíveis.
4. Marcar conflito ou obsolescência; não apagar silenciosamente.
5. Criar ou editar somente quando houver autorização explícita.
6. Validar ausência de GUID, nome ou definição duplicados.

## Pacote obrigatório por disciplina

Ao finalizar cada disciplina e ao encerrar cada sessão, gerar ou atualizar:

1. `revit_user_defined_psets_<disciplina>.txt`;
2. `ids_<disciplina>.ids`;
3. `export_interbility_tools_<disciplina>.xml`;
4. `bonsai_csv_config_<disciplina>.json`.

Executar `scripts/generate_conjunto_packages.js` quando a disciplina estiver
suportada pelo gerador. Usar a pasta `Conjunto` por padrão. Se o usuário definir
um destino em `D:`, confirmar que a unidade e o caminho existem antes de gravar;
nunca inventar ou substituir silenciosamente por outro caminho.

## Validação mínima do pacote

- XML e IDS bem formados.
- JSON parseável.
- Nenhuma ocorrência ou vinculação a `Generic Models`.
- Nenhum Pset customizado iniciado por `Pset_`.
- Nomes e GUIDs referenciados existentes no arquivo compartilhado aprovado.
- Um único destino por parâmetro.
- Qto oficial não duplicado em Pset customizado.
- IDS `0/0` reportado como falha de cobertura, nunca como conformidade.
- Registrar limitações quando não houver validação contra o XSD IDS ou contra um
  IFC exportado.
