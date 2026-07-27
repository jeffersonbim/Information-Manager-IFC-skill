# Guia operacional — seis gates para requisitos e validação IFC

Este guia conduz uma solicitação de informação desde a decisão que ela apoia até a comprovação no IFC. O objetivo não é burocratizar o BIM: é evitar que um dado seja modelado, exportado e validado sem que sua finalidade e seu destino estejam claros.

O recorte é técnico. Este processo não trata da gestão de um CDE. Ele trata da qualidade da informação, da tradução Revit–IFC e da validação do modelo entregue.

## Visão do fluxo

`PIR → EIR → requisito de informação → origem Revit → destino IFC → exportação comprovada → IDS → modelo validado`

O PIR esclarece **qual decisão precisa de informação**. O EIR traduz essa necessidade em exigências técnicas, gerenciais e comerciais de produção. O IDS representa apenas a parte do EIR que pode ser verificada automaticamente no IFC.

Cada gate tem uma pergunta principal. Se a resposta for “não”, a linha retorna ao ponto em que a decisão ainda pode ser corrigida.

| Gate | Pergunta que protege o fluxo | Saída mínima |
|---|---|---|
| 1. Requisitos | O pedido está claro e apoia uma decisão? | Requisito estruturado e justificado |
| 2. Origem | O dado já existe no Revit? | Origem nativa, compartilhada ou customizada definida |
| 3. Arquitetura | O caminho Revit–IFC foi aprovado? | Mapeamento técnico decidido |
| 4. Exportação | O dado chegou corretamente ao IFC? | Evidência no IFC real |
| 5. IDS | A regra pode virar IDS? | IDS por disciplina, pronto para execução |
| 6. Validação | O modelo atende ao requisito? | Resultado, evidência e rota de correção |

---

## Gate 1 — Requisitos de informação

**Pergunta orientadora:** qual decisão esse dado deve apoiar?

O Gate 1 começa no PIR. Antes de perguntar em qual parâmetro o dado será gravado, a equipe precisa entender por que ele é necessário. Isso impede pedidos como “incluir material” sem contexto, unidade, categoria ou critério de aceite.

### Passo a passo

1. Registre a decisão que precisa ser apoiada. Exemplo: “verificar o vão e a identificação das portas para compatibilização e entrega”.
2. Dê um código único ao requisito. Exemplo: `EX-ARQ-PORTA-001`.
3. Informe o nome do campo pedido pelo cliente. Exemplo: `Largura`.
4. Descreva o significado do dado e a finalidade de uso. Não repita apenas o nome do campo.
5. Defina disciplina e categoria Revit. Exemplo: Arquitetura e `Doors`.
6. Declare o schema IFC da entrega. Exemplo: `IFC2X3` ou `IFC4`.
7. Complete unidade, tipo de dado, cardinalidade, valores permitidos e fase de obrigatoriedade quando já forem conhecidos.
8. Revise os campos essenciais do template: `Codigo_Requisito`, `Descricao`, `Disciplina`, `Categoria_Revit` e `Schema_IFC`.

### Saída do gate

Uma linha de requisito que permite a pesquisa técnica. A linha não precisa conhecer ainda o Pset ou o Qto, mas não pode estar sem categoria, descrição, disciplina ou schema.

### Rota se não aprovar

Retorne ao solicitante ou à coordenação para esclarecer a decisão, a categoria aplicável ou o critério de aceitação. Não avance uma linha ambígua para o mapeamento.

---

## Gate 2 — Origem no Revit

**Pergunta orientadora:** o dado já existe no Revit e em que escopo?

Aqui a equipe pesquisa a origem do dado. A prioridade é reutilizar informação nativa e consistente. Um parâmetro compartilhado só deve ser criado quando o Revit não representa o conceito solicitado ou quando a padronização entre famílias e disciplinas exige isso.

### Passo a passo

1. Abra uma família ou um modelo de referência da categoria solicitada.
2. Pesquise o parâmetro nativo aplicável: instância, tipo, sistema ou material.
3. Compare o significado do parâmetro com o requisito, não apenas o nome. `Width` pode ser adequado para largura de porta; não é automaticamente adequado para qualquer largura solicitada.
4. Registre o candidato em `Parametro_Revit_Candidato`.
5. Registre `Origem_Revit_Tipo` e `Escopo_Revit`: nativo/compartilhado; instância/tipo/sistema.
6. Caso não exista origem adequada, proponha um parâmetro compartilhado com nome claro, grupo, tipo de dado e GUID.
7. Evite criar um parâmetro customizado que apenas duplica um campo nativo ou uma quantidade calculável.
8. Atualize o artefato. Quando houver uma correspondência conhecida, ele pode apresentar uma proposta automática; a proposta ainda deve ser revisada.

### Exemplo — porta

Para o requisito `Largura`, a proposta inicial pode ser:

| Campo | Proposta |
|---|---|
| Origem Revit | `Width` |
| Escopo | Tipo ou instância, conforme a família e a regra do projeto |
| Unidade | mm |
| Tipo de dado | Comprimento |
| Cardinalidade | `1..1` quando for obrigatório em toda porta aplicável |

### Saída do gate

Origem Revit definida como nativa, compartilhada ou customizada, com o escopo correto.

### Rota se não aprovar

Se não há parâmetro existente, crie uma proposta de parâmetro compartilhado. Se a necessidade não está suficientemente definida, volte ao Gate 1.

---

## Gate 3 — Arquitetura do mapeamento IFC

**Pergunta orientadora:** o caminho Revit–IFC é tecnicamente apropriado e foi aprovado?

Este gate decide onde o dado deve aparecer no IFC. A decisão não parte do nome do parâmetro Revit; parte do conceito e do schema de entrega.

### Passo a passo

1. Confirme a classe IFC da categoria. Exemplo: uma porta normalmente é entregue como `IfcDoor`.
2. Verifique se o conceito existe como atributo IFC. Para uma porta, largura e altura podem ser tratadas pelos atributos `OverallWidth` e `OverallHeight` quando aplicáveis ao schema e à exportação.
3. Se não for atributo, verifique o Pset oficial aplicável à classe e ao `PredefinedType`.
4. Se o dado for uma grandeza mensurável, avalie o Qto padrão antes de criar propriedade textual.
5. Se o requisito tratar do material efetivo, prefira associação de material a repetir o nome do material em um Pset.
6. Use Pset customizado apenas para informação descritiva que não tem destino padronizado. Nomeie o conjunto por domínio, por exemplo `Pset_Esquadrias.LarguraBatente`; não use um Pset para “esconder” uma quantidade padrão.
7. Registre o destino: `ATTRIBUTE`, `STANDARD_PSET`, `STANDARD_QTO`, `CUSTOM_PSET` ou `MATERIAL_ASSOCIATION`.
8. Complete os campos do destino: atributo, Pset e propriedade, ou Qto e quantidade, conforme a escolha.
9. Defina a regra de aceitação que será verificada depois.

### Exemplo — porta

| Requisito | Origem Revit candidata | Destino IFC proposto |
|---|---|---|
| Altura | `Height` | `ATTRIBUTE` → `OverallHeight` |
| Largura | `Width` | `ATTRIBUTE` → `OverallWidth` |
| Área | `Area` | `STANDARD_QTO` → `Qto_DoorBaseQuantities.Area` |
| Material | `Material` | `MATERIAL_ASSOCIATION` |
| Código PP | `Mark` | `ATTRIBUTE` → `Tag`, sujeito à prova de exportação |

### Saída do gate

Mapeamento aprovado, com origem Revit, classe IFC, tipo de destino e regra de aceite explicitados.

### Rota se não aprovar

Quando houver mais de um destino possível, mantenha a linha em revisão técnica. Quando o conceito não tiver destino padrão, defina um Pset customizado e registre a justificativa. Não siga para a exportação sem essa decisão.

---

## Gate 4 — Exportação e prova no IFC

**Pergunta orientadora:** o dado chegou ao IFC real, com o nome, a estrutura e o valor esperados?

Configuração de exportação não é prova. A prova é a inspeção de um IFC produzido a partir de um modelo de teste controlado.

### Passo a passo

1. Prepare um modelo de teste com elementos da categoria e valores conhecidos.
2. Configure o exportador Revit de acordo com o mapeamento aprovado.
3. Exporte no schema definido pelo requisito.
4. Abra o IFC em um visualizador ou ferramenta de inspeção IFC.
5. Localize o elemento pelo `GlobalId` e confirme a classe IFC.
6. Confirme a presença do atributo, Pset, Qto ou associação de material definidos no Gate 3.
7. Compare valor, unidade e tipo de dado com a origem Revit.
8. Registre evidência: arquivo, data, versão do exportador, `GlobalId`, captura ou relatório de inspeção.
9. Ajuste o mapeamento e repita a exportação quando o dado não chegar como esperado.

### Saída do gate

Evidência de que o caminho escolhido funciona no IFC real. Só depois disso a regra pode ser formalizada para validação automática.

### Rota se não aprovar

Se a origem Revit está correta, mas o IFC não recebeu o dado, retorne ao Gate 3 e ajuste o mapeamento ou a configuração de exportação. Se a origem está errada, retorne ao Gate 2.

---

## Gate 5 — Formalização em IDS

**Pergunta orientadora:** a parte verificável do requisito pode ser expressa em IDS?

O IDS não substitui o EIR. Ele formaliza regras objetivas que podem ser avaliadas no IFC: aplicabilidade, presença, valor, tipo e, quando aplicável, enumerações.

### Passo a passo

1. Separe o que é automaticamente verificável do que depende de julgamento humano.
2. Crie um IDS por disciplina ou por pacote lógico de requisitos.
3. Defina a aplicabilidade: classe IFC, `PredefinedType`, classificação ou outra condição necessária.
4. Transcreva apenas o destino comprovado no Gate 4.
5. Defina se o requisito é obrigatório, facultativo ou proibido para cada população aplicável.
6. Configure testes de presença, tipo de dado, unidade e valor permitido quando isso estiver definido.
7. Registre a versão do IDS e a relação com os códigos de requisito.
8. Execute um teste inicial no IFC de referência e revise falsos positivos ou falsos negativos.

### Saída do gate

IDS revisado, por disciplina, capaz de testar apenas regras efetivamente comprovadas no IFC.

### Rota se não aprovar

Se a regra depende de informação que não chegou ao IFC, volte ao Gate 4. Se ela depende de interpretação humana, mantenha-a fora do IDS e crie uma verificação manual documentada.

---

## Gate 6 — Validação e decisão sobre o modelo

**Pergunta orientadora:** o modelo entregue atende aos requisitos aplicáveis?

O Gate 6 consolida o resultado. Ele não deve mostrar apenas percentuais: precisa apontar a linha reprovada, o requisito, o elemento, o valor encontrado e a origem da correção.

### Passo a passo

1. Carregue o IFC da disciplina e o IDS aprovado.
2. Execute a validação e gere o relatório por disciplina.
3. Registre arquivo analisado, data, schema, versão do IDS e resultado.
4. Para cada falha, registre código do requisito, `GlobalId`, classe IFC, valor esperado, valor encontrado e motivo.
5. Classifique o resultado como conforme, não conforme ou inconclusivo.
6. Direcione a correção: Gate 1 para requisito incompleto; Gate 2 para origem Revit; Gate 3 para decisão de mapeamento; Gate 4 para exportação; Gate 5 para regra IDS.
7. Reexporte e revalide somente depois de corrigir a causa.
8. Atualize o consolidado com o último modelo analisado de cada disciplina.

### Saída do gate

Modelo validado, não conforme com rota de correção, ou inconclusivo com evidência insuficiente identificada.

### Rota se não aprovar

Não conformidade não é encerramento: é uma devolução ao gate de origem. A correção deve atacar a causa, não apenas editar o IFC entregue.

---

## Checklist de fechamento do ciclo

- Todo requisito possui código, finalidade e categoria aplicável.
- A origem Revit está definida como nativa, compartilhada ou customizada.
- O destino IFC foi decidido e comprovado no arquivo exportado.
- O IDS contém somente regras que podem ser verificadas automaticamente.
- Cada falha possui requisito, `GlobalId`, motivo e gate de retorno.
- O consolidado considera o último relatório analisado por disciplina.

Todo dado precisa de um destino. Toda decisão, de uma evidência.

## Referências de base

- ISO 19650-1, termos e conceitos de OIR, PIR, AIR e EIR; processo de gestão da informação.
- buildingSMART, IFC e IDS: classes, atributos, conjuntos de propriedades, quantidades e Information Delivery Specification.
