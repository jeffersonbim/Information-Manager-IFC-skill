# Questionário técnico dos seis gates

## Finalidade

Usar as perguntas como orientação obrigatória antes da decisão de cada gate.
Elas não substituem a evidência determinística e não ampliam o fluxo para CDE,
nomeação de documentos ou gestão contratual. O recorte termina no modelo IFC
validado contra os requisitos técnicos aplicáveis.

## Protocolo de interação

1. Identificar o gate atual e apresentar sua pergunta de decisão.
2. Perguntar ao usuário as questões `G<n>-Q1` a `G<n>-Q5`.
3. Aceitar respostas objetivas, inclusive `desconhecido`, `não definido` ou
   `não aplicável`, sem completar lacunas por inferência.
4. Resumir as respostas e pedir confirmação quando houver ambiguidade.
5. Validar a completude com `scripts/gate_questionnaire.py`.
6. Prosseguir somente quando as respostas obrigatórias e as evidências de saída
   do gate estiverem presentes.

## Estados permitidos

- `READY`: todas as perguntas obrigatórias foram respondidas e nenhuma lacuna
  impede a análise técnica.
- `REVIEW`: as perguntas foram respondidas, mas existe decisão semântica,
  conflito ou aprovação humana pendente.
- `BLOCKED`: falta resposta obrigatória ou uma lacuna impede produzir a
  evidência de saída.

Uma resposta textual não aprova o gate. A passagem exige a condição de saída
definida no processo e sua evidência rastreável.

## Privacidade

Não registrar nomes pessoais, caminhos originais, conteúdo sensível do IFC ou
credenciais nas respostas. Para arquivos IFC/STEP, usar somente identificadores
opacos e hashes conforme o privacy gate.

## Fonte canônica

As perguntas e seus identificadores são mantidos em
`references/gates-questionnaire.json`. Dashboard, artigo e agentes devem usar o
mesmo texto e a mesma numeração.
