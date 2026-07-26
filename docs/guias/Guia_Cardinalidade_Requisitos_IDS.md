# Guia técnico — cardinalidade em requisitos BIM e IDS

## 1. O que é cardinalidade

Cardinalidade responde à pergunta:

> Quantos valores esse requisito permite ou exige para cada objeto aplicável?

Ela não define qual deve ser o valor. Define:

- se a informação pode estar ausente;
- se a informação é obrigatória;
- se pode existir apenas um valor;
- se podem existir vários valores.

A representação geral é:

`mínimo..máximo`

## 2. Como interpretar

| Cardinalidade | Interpretação |
|---|---|
| `0..1` | O dado é opcional; se existir, admite no máximo um valor |
| `1` ou `1..1` | O dado é obrigatório e admite exatamente um valor |
| `0..n` | O dado é opcional e pode admitir vários valores |
| `1..n` | Deve existir pelo menos um valor e podem existir vários |

O primeiro número define a quantidade mínima:

- `0`: a ausência é permitida;
- `1`: pelo menos um valor é obrigatório.

O segundo termo define a quantidade máxima:

- `1`: somente um valor;
- `n`: vários valores.

## 3. Por que isso é necessário

Sem cardinalidade, a frase “a porta deve possuir resistência ao fogo” continua
ambígua. Não está claro se:

- o campo é obrigatório para todas as portas;
- é obrigatório somente para portas corta-fogo;
- é opcional para as demais;
- pode conter um ou vários valores.

A cardinalidade permite transformar a intenção em uma condição verificável.
Ela evita:

- reprovar dados realmente opcionais;
- aprovar objetos sem um dado obrigatório;
- permitir vários valores quando deveria existir apenas um;
- criar um IDS que não corresponde ao requisito do cliente.

## 4. Cardinalidade e população aplicável

A cardinalidade deve ser interpretada dentro da população definida pela
`applicability`.

Exemplo:

> Portas corta-fogo devem possuir resistência ao fogo.

Uma implementação adequada separa:

- **applicability:** quais portas são consideradas corta-fogo;
- **requirement:** qual propriedade representa a resistência;
- **cardinalidade:** quantos valores dessa propriedade devem existir para cada
  porta aplicável.

Se `FireRating` for obrigatório para todas as portas corta-fogo, a cardinalidade
do requirement é `1`.

Portas comuns devem ficar fora da população quando o requisito não se aplica a
elas. Não se deve usar `0..1` somente para esconder uma applicability mal
definida.

## 5. Existência do parâmetro não significa atendimento

Devem ser verificadas separadamente:

1. existência do parâmetro no Revit;
2. presença e preenchimento no modelo autoral;
3. exportação para o destino IFC planejado;
4. presença do valor no IFC;
5. atendimento à cardinalidade definida;
6. atendimento ao datatype, unidade e valores permitidos.

Um parâmetro pode existir no Revit e estar vazio. O exportador também pode não
serializar campos vazios. Por isso, a cardinalidade precisa ser verificada no
IFC real, e não apenas na configuração do modelo autoral.

## 6. Roteiro de decisão

Para cada requisito e cada objeto aplicável, perguntar:

### Pergunta 1

> Se o dado estiver ausente, o objeto deve reprovar?

- **Sim:** o mínimo é `1`.
- **Não:** o mínimo é `0`.

### Pergunta 2

> O objeto pode possuir mais de um valor válido para esse requisito?

- **Sim:** o máximo é `n`.
- **Não:** o máximo é `1`.

As respostas produzem:

| Ausência reprova? | Vários valores? | Cardinalidade |
|---|---|---|
| Não | Não | `0..1` |
| Sim | Não | `1` |
| Não | Sim | `0..n` |
| Sim | Sim | `1..n` |

## 7. Exemplos BIM

As cardinalidades abaixo são pontos de partida. O requisito aprovado pelo
cliente continua sendo a fonte da obrigatoriedade.

| Categoria | Informação | Cardinalidade inicial | Justificativa |
|---|---|---:|---|
| Parede | Código do tipo | `1` | Um identificador obrigatório por tipo |
| Parede | Materiais das camadas | `1..n` | Uma parede pode possuir várias camadas |
| Porta | Largura total | `1` | Uma largura principal por porta aplicável |
| Porta | Altura total | `1` | Uma altura principal por porta aplicável |
| Porta | Possui bandeira | `1` | Booleano explícito quando o conceito fizer parte do requisito |
| Porta | Largura da bandeira | `0..1` | Só existe quando há bandeira |
| Porta corta-fogo | Resistência ao fogo | `1` | Obrigatória para a população corta-fogo |
| Janela | Largura | `1` | Uma largura principal |
| Janela | Material | `1..n` | Pode haver mais de um material associado |
| Guarda-corpo | Tipo de fixação | `1` | Quando exigido para todos os aplicáveis |
| Viga | Material estrutural principal | `1` | Um material principal por objeto, conforme a regra adotada |
| Pilar | Resistência ao fogo | `0..1` ou `1` | Depende da população, fase e requisito |
| Piso | Área | `1` | Uma quantidade segundo o método de medição aprovado |
| Elemento | Classificações | `0..n` ou `1..n` | Pode admitir múltiplos sistemas classificatórios |

## 8. Exemplo detalhado: porta com bandeira

Considere a população de todas as portas de uma disciplina:

| Informação | Cardinalidade | Interpretação |
|---|---:|---|
| Código | `1` | Toda porta aplicável precisa de um código |
| Largura total | `1` | Exatamente uma largura principal |
| Altura total | `1` | Exatamente uma altura principal |
| Possui bandeira | `1` | O modelo precisa declarar Sim ou Não |
| Largura da bandeira | `0..1` | Ausente quando não há bandeira |
| Altura da bandeira | `0..1` | Ausente quando não há bandeira |
| Material da bandeira | `0..n` | Pode não existir ou admitir múltiplos materiais |

Uma validação mais precisa pode criar uma segunda população:

> Portas cujo campo `PossuiBandeira` seja verdadeiro.

Nessa população, largura e altura da bandeira podem ter cardinalidade `1`,
porque sua ausência deve reprovar a porta.

Esse exemplo demonstra que uma boa applicability pode transformar um campo
globalmente opcional em obrigatório dentro da população correta.

## 9. Cardinalidade não substitui outras regras

Mesmo com cardinalidade `1`, ainda é necessário validar:

- datatype;
- unidade;
- faixa ou enumeração de valores;
- padrão de texto;
- classe IFC e `PredefinedType`;
- Pset, propriedade, atributo ou Qto;
- nível de tipo ou ocorrência;
- fase de obrigatoriedade.

Exemplo:

`FireRating = "qualquer texto"` pode atender à presença `1`, mas reprovar a
lista de valores permitidos.

## 10. Relação com os seis gates

### Gate 1 — Requisitos

Definir a cardinalidade pretendida e a população aplicável.

### Gate 2 — Origem

Verificar se a origem autoral consegue produzir a quantidade de valores
necessária.

### Gate 3 — Arquitetura

Confirmar compatibilidade entre escopo Revit, datatype, destino IFC e
cardinalidade.

### Gate 4 — Exportação

Comprovar como valores presentes, ausentes e múltiplos são serializados no IFC.

### Gate 5 — IDS

Representar a obrigatoriedade na applicability e nos requirements, testando
casos positivo, negativo e não aplicável.

### Gate 6 — Validação

Relatar população, aplicáveis, aprovados, reprovados, não avaliados e cobertura.

## 11. Como preencher a planilha

Na coluna `Cardinalidade` da aba `Entrada_Requisitos`:

1. avaliar somente os objetos da população aplicável;
2. decidir se a ausência deve reprovar;
3. decidir se múltiplos valores são legítimos;
4. registrar `0..1`, `1`, `0..n` ou `1..n`;
5. documentar exceções em `Criterio_Aceitacao` ou `Observacoes`;
6. confirmar a interpretação com o responsável pelo requisito.

Quando a cardinalidade não puder ser determinada, não presumir um valor. Usar
o estado de revisão e retornar ao Gate 1.

