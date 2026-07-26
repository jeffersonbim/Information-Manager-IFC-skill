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

## 12. Código do requisito, nome do campo e destino IFC

`Codigo_Requisito` não é o nome do parâmetro. É o identificador permanente da
exigência e deve permanecer estável mesmo quando o nome recebido for corrigido,
normalizado ou mapeado.

Exemplo:

| Campo | Valor |
|---|---|
| `Codigo_Requisito` | `ARQ-PORTA-001` |
| `Nome_Campo_Cliente` | `LarguraBandeira` |
| `Descricao` | Largura da bandeira superior da porta |
| `Parametro_Revit_Candidato` | `BIM_LarguraBandeira` |
| `Origem_Revit_Tipo` | `INEXISTENTE` até criação aprovada |
| `Categoria_Revit` | `Doors` |
| `Unidade` | `mm` |
| `Cardinalidade` | `0..1` |

Devem ser preservados separadamente:

1. **Código do requisito:** chave de rastreabilidade nos seis gates.
2. **Nome do campo do cliente:** texto exato recebido.
3. **Parâmetro Revit candidato:** possível origem autoral.
4. **Destino IFC:** estrutura final aprovada e comprovada.

## 13. Nativo IFC não significa Pset

Um dado nativo IFC não precisa começar com `Pset_`. O schema possui estruturas
diferentes:

| Destino | Exemplo |
|---|---|
| Atributo | `IfcDoor.OverallWidth` |
| Quantity Set | `Qto_DoorBaseQuantities.Width`, quando aplicável ao schema |
| Property Set | `Pset_DoorCommon.FireRating` |
| Associação | `IfcRelAssociatesMaterial` |

A pesquisa deve seguir a prioridade:

1. `ATTRIBUTE`;
2. `STANDARD_QTO`;
3. `STANDARD_PSET`;
4. `MATERIAL_ASSOCIATION`;
5. `CUSTOM_QTO`;
6. `CUSTOM_PSET`;
7. `CALCULATED_ONLY`;
8. `UNVERIFIED`.

O prefixo `Pset_` identifica um conjunto de propriedades. Ele não representa
atributos nativos, quantidades ou associações. Um conjunto customizado também
não deve copiar o nome de um Pset oficial.

## 14. Como registrar um candidato de Qto

Na entrada, registrar separadamente:

- `Destino_IFC_Tipo_Candidato`: `STANDARD_QTO` ou `CUSTOM_QTO`;
- `QuantitySet_Candidato`;
- `QuantityName_Candidato`;
- schema e classe IFC candidatos.

Na saída da análise, completar:

- `QuantityType`;
- `MethodOfMeasurement`;
- `Formula_Calculo`;
- `Datatype_IFC`;
- `Entidade_Exportada_Comprovada`;
- `Evidencia_Inspecao_IFC`.

Exemplo para uma área de piso:

| Campo | Valor |
|---|---|
| `Codigo_Requisito` | `ARQ-FLOOR-001` |
| `Nome_Campo_Cliente` | `AreaPiso` |
| `Parametro_Revit_Candidato` | `Area` |
| `Origem_Revit_Tipo` | `NATIVO` |
| `Schema_IFC` | `IFC4.3` |
| `Classe_IFC_Candidata` | `IfcSlab` |
| `Destino_IFC_Tipo_Candidato` | `STANDARD_QTO` |
| `QuantityName_Candidato` | `GrossArea` ou `NetArea`, conforme requisito |
| `QuantityType` | `IfcQuantityArea` |
| `Entidade_Exportada_Comprovada` | `IfcElementQuantity > IfcQuantityArea` |

O nome exato do `QuantitySet` deve ser confirmado na versão do schema. Não
preencher automaticamente um nome de IFC4/IFC4.3 quando a entrega for IFC2X3.

## 15. Exemplos de destinos diferentes

### Largura total da porta

- origem: parâmetro nativo de largura no Revit;
- destino: `ATTRIBUTE`;
- atributo: `IfcDoor.OverallWidth`;
- Qto e Pset permanecem vazios, salvo requisito adicional justificado.

### Resistência ao fogo

- origem: `Fire Rating` no Revit;
- destino: `STANDARD_PSET`;
- Pset: `Pset_DoorCommon`;
- propriedade: `FireRating`.

### Largura da bandeira

- origem: parâmetro compartilhado candidato;
- destino inicial: `UNVERIFIED`;
- destino possível: `CUSTOM_QTO` quando for medição contratual ou
  `CUSTOM_PSET` quando for informação descritiva;
- aprovação: somente após o Gate 4 comprovar a entidade realmente exportada.

O parâmetro Revit é a origem do dado. Atributo, Qto, Pset e associação são
destinos IFC diferentes.

## 16. Entendendo Pset e Qto de forma prática

### O que é um Pset

`Pset` significa **Property Set**, ou conjunto de propriedades. Ele organiza
informações que descrevem uma característica, condição ou classificação do
objeto.

Exemplos:

- `Pset_DoorCommon.FireRating`: resistência ao fogo da porta;
- `Pset_DoorCommon.IsExternal`: indica se a porta é externa;
- `Pset_WallCommon.LoadBearing`: indica se a parede possui função estrutural.

O nome completo possui dois níveis:

```text
Pset_DoorCommon.FireRating
└── conjunto         └── propriedade
```

O Pset não é o parâmetro do Revit. O parâmetro Revit é uma possível fonte do
valor; o Pset e sua propriedade constituem o destino desse valor no IFC.

### O que é um Qto

`Qto` significa **Quantity Set**, ou conjunto de quantidades. Ele agrupa
medições do objeto, como comprimento, largura, altura, área, volume, perímetro,
peso ou contagem.

Exemplos:

- `Qto_SlabBaseQuantities.GrossArea`: área bruta de uma laje;
- `Qto_WallBaseQuantities.NetVolume`: volume líquido de uma parede;
- `Qto_DoorBaseQuantities.Width`: largura quantificada de uma porta, quando
  prevista pelo schema contratado.

O nome também possui dois níveis:

```text
Qto_SlabBaseQuantities.GrossArea
└── conjunto de quantidades └── quantidade
```

Uma quantidade IFC possui ainda um tipo técnico, como `IfcQuantityLength`,
`IfcQuantityArea`, `IfcQuantityVolume`, `IfcQuantityWeight` ou
`IfcQuantityCount`.

### Diferença essencial

| Pergunta | Usar preferencialmente |
|---|---|
| É uma característica ou condição do objeto? | `Pset` |
| É uma medição do objeto? | `Qto` |
| É parte da identidade ou geometria fundamental da entidade IFC? | atributo IFC |
| É uma relação com material, classificação ou documento? | associação IFC |

Exemplo: `FireRating` é uma característica e tende a ser mapeado em Pset.
`GrossArea` é uma medição e tende a ser mapeada em Qto. `OverallWidth`, quando
definido como atributo da entidade no schema adotado, deve ser tratado como
atributo e não duplicado automaticamente em um Pset customizado.

### Pset e Qto podem existir juntos?

Sim. O mesmo objeto pode possuir simultaneamente:

- atributos da entidade IFC;
- Psets padronizados;
- Qto padronizados;
- associações de material ou classificação;
- conjuntos customizados aprovados pelo projeto.

Isso não significa que o mesmo requisito deva ser repetido em todos eles. Cada
requisito deve ter um destino principal, escolhido segundo o schema, a
finalidade de uso e a evidência da exportação.

### Quando criar estrutura customizada

Uma estrutura customizada somente deve ser adotada quando:

1. o requisito é contratualmente necessário;
2. não existe destino padronizado adequado no schema contratado;
3. o dado pode ser produzido e mantido de forma confiável;
4. a regra de nomeação foi aprovada;
5. a exportação foi testada no IFC;
6. o IDS consegue validar o destino efetivamente exportado.

Para informação descritiva, usar `CUSTOM_PSET`. Para medição contratual sem
destino padronizado, avaliar `CUSTOM_QTO`. Se a exportação ainda não estiver
comprovada, registrar `UNVERIFIED`, nunca assumir o destino.

### Regra de decisão para o Gate 2

Para cada requisito, responder nesta ordem:

1. Existe atributo IFC apropriado?
2. Se for medição, existe Qto padronizado no schema contratado?
3. Se for propriedade, existe Pset padronizado?
4. Existe associação IFC mais adequada?
5. A criação de Qto ou Pset customizado é indispensável?
6. O exportador realmente produz essa estrutura?

O IDS deve ser criado depois dessa decisão. Ele valida o dado no destino IFC;
não transforma um parâmetro Revit em Pset ou Qto.
