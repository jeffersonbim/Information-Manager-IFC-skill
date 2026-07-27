# Nota conceitual — PIR, EIR e os gates técnicos

Status: conceito aprovado para integração posterior no artigo, apresentação,
dashboard e documentação do fluxo.

Referência primária: ABNT NBR ISO 19650-1:2022, versão corrigida de 26.11.2024,
especialmente 3.3.5, 3.3.6, Seção 5 e Figura 2.

## Correção do ponto de partida

O fluxo técnico não começa no EIR. A necessidade surge antes, no nível dos
requisitos de informação que orientam decisões.

- **OIR**: requisitos de informação relacionados aos objetivos organizacionais.
- **AIR**: requisitos de informação relacionados à operação do ativo.
- **PIR**: requisitos de informação do projeto relacionados à entrega do ativo.
  O PIR detalha as informações necessárias para responder ou informar decisões
  estratégicas relativas ao ativo a ser construído. Deve existir um conjunto
  coerente para cada ponto-chave de decisão da contratante.
- **EIR**: requisitos de troca da informação relacionados a uma contratação.
  Detalham os aspectos gerenciais, comerciais e técnicos da produção da
  informação e devem ser capazes de responder ao PIR.

Não representar OIR, AIR, PIR e EIR como uma cadeia universal estritamente
linear. A Figura 2 da ABNT NBR ISO 19650-1 utiliza relações como “delimita”,
“contribui” e “especifica”. Para este fluxo, a leitura didática adotada é:

```text
OIR — objetivos organizacionais ─┐
                                 ├── contribuem para o PIR
AIR — necessidades do ativo ─────┘
                                          │
                                          ▼
PIR — o que a contratante precisa saber em cada decisão
                                          │
                                          ▼
EIR — como a troca será especificada na contratação
```

Essa simplificação deve ser acompanhada da ressalva de que a hierarquia
normativa completa não é uma sequência documental única.

## Repercussão nos gates

### Gate 1 — Requisitos

Trabalha no nível do **PIR**:

- qual decisão será informada;
- por que a informação é necessária;
- em qual ponto-chave de decisão ela deve estar disponível;
- quais objetos ou sistemas são aplicáveis;
- qual é o nível mínimo de informação necessário;
- como será reconhecido que a necessidade foi atendida.

Pergunta de decisão revisada:

> Está claro qual decisão este requisito deve informar e qual informação é
> necessária para respondê-la?

Condição de saída:

> requisito vinculado a uma decisão, com finalidade, aplicabilidade, momento e
> critério de aceitação definidos.

### Gates 2 e 3 — Tradução para a troca

Fazem a ponte entre o PIR e os aspectos técnicos do **EIR**:

- localizar origem autoral;
- localizar destino IFC;
- definir categoria, classe, unidade, datatype e cardinalidade;
- decidir entre atributo, Pset, Qto ou associação;
- aprovar a matriz Revit–IFC;
- definir como a informação será produzida e trocada.

### Gate 4 — Comprovação da capacidade de entrega

Demonstra que a solução técnica definida para a troca consegue produzir no IFC
real a informação necessária para responder ao PIR.

### Gate 5 — Formalização verificável

O **IDS não equivale ao EIR**. Ele pode formalizar a parcela técnica,
estruturada e verificável dos requisitos de troca.

O Gate 5 deve:

- transformar requisitos já comprovados no IFC em regras IDS;
- registrar aplicabilidade, cardinalidade e critério de aceitação;
- reconhecer que aspectos gerenciais, comerciais, documentais ou não
  estruturados do EIR permanecem fora do alcance do IDS.

### Gate 6 — Validação e retorno à decisão

Avalia se o modelo entregue contém a informação necessária e produz evidências
para a decisão que originou o PIR.

O resultado não é apenas “o IDS passou”. O resultado deve permitir afirmar:

- se a informação necessária está presente;
- qual foi a cobertura da verificação;
- quais objetos falharam;
- se a decisão pode ser informada;
- se o resultado é conforme, não conforme ou inconclusivo.

## Regra editorial

Substituir em todos os materiais a narrativa:

> EIR → parâmetros → IDS → IFC

por:

> decisão → PIR → especificação de troca/EIR → implementação e prova no IFC →
> formalização verificável/IDS → modelo validado → evidência para a decisão

