---
name: ifc-especialista
description: Orienta como parametrizar corretamente tipos/familias do Revit para exportacao IFC (IfcExportAs, Type IFC Predefined Type), evitando categorias vazias, duplicadas ou invalidas. Cobre tambem como criar e validar arquivos IDS (Information Delivery Specification, buildingSMART) para exigir parametros obrigatorios no modelo, incluindo os erros de schema mais comuns. Usar quando o usuario for configurar parametros IFC de familias no Revit antes de exportar, revisar Categoria/PredefinedType de um IFC ja exportado, criar/validar um .ids, ou usar Classification Manager / Model Checker / IFC Tester.
---

# Parametrizacao IFC no Revit

## Diagnostico rapido (fazer antes de mexer em qualquer parametro)

1. Pega elemento de exemplo da categoria (ex: 1 porta).
2. Confere os 3 campos no Type Properties, secao "IFC Parameters":
   - `Export Type to IFC As` (nome da classe IFC, ex: `IfcDoorType`)
   - `Type IFC Predefined Type` (enum da categoria, ex: `DOOR`)
   - `IFCExportAs` (texto combinado `IfcClasse.CATEGORIA`, ex: `IfcDoor.DOOR`)
3. Os 3 tem que **bater entre si**. Se um disser `IfcDoorType`/`DOOR` e outro `IfcCovering.TERRAIN`, tem conflito -- exportador nao sabe qual usar.

## Formato correto do IFCExportAs

```
IfcClasse.CATEGORIA
```

Exemplo: `IfcDoor.DOOR`, `IfcWindow.WINDOW`, `IfcRailing.GUARDRAIL`.

Erros comuns encontrados na pratica:
- Usar **material** como categoria (`IfcDoor.WOOD` -- errado, WOOD nao existe no enum de porta, material e' propriedade separada, ja fica correto via associacao de material do Revit).
- Deixar **USERDEFINED** quando existe enum real disponivel (joga fora classificacao padrao a toa; USERDEFINED so' e' certo quando o elemento genuinamente nao se encaixa em nenhuma categoria do IFC).
- Usar classe **exclusiva do IFC4** (ex: `IfcGeographicElement`) num projeto exportando como **IFC2x3** -- a entidade nao existe nesse schema, export falha ou e' descartado silenciosamente. Confere o schema do projeto antes (Export IFC > Modify Setup > aba File, campo "IFC Version").
- Os 3 campos (Export Type to IFC As / Type IFC Predefined Type / IFCExportAs) com valores **inconsistentes** entre si.

## Enums validos mais comuns (IFC2x3)

| Classe | Enum valido |
|---|---|
| IfcDoor | DOOR, GATE, TRAPDOOR, USERDEFINED, NOTDEFINED |
| IfcWindow | WINDOW, SKYLIGHT, LIGHTDOME, USERDEFINED, NOTDEFINED |
| IfcRailing | HANDRAIL, GUARDRAIL, BALUSTRADE, USERDEFINED, NOTDEFINED |
| IfcCovering | CEILING, CLADDING, FLOORING, INSULATION, MEMBRANE, MOLDING, ROOFING, USERDEFINED, NOTDEFINED |
| IfcWall | STANDARD, POLYGONAL, SHEAR, ELEMENTEDWALL, PLUMBINGWALL, USERDEFINED, NOTDEFINED |
| IfcSlab | FLOOR, ROOF, LANDING, BASESLAB, USERDEFINED, NOTDEFINED |
| IfcMember | MULLION, PLATE, STIFFENER, ... USERDEFINED, NOTDEFINED |

Se a categoria nao tiver enum bom o suficiente pra descrever o elemento (ex: grama, elemento de paisagismo em IFC2x3), usa `USERDEFINED` mesmo e deixa a descricao real no campo de texto livre (ObjectType/Description) -- nesse caso e' o uso correto, nao gambiarra.

**Fallback de 2 niveis** (confirmado pelo Protocolo BIM PR, norma oficial -- ver secao
propria abaixo): se nem a classe IFC certa existir no software/mapeamento, o fallback nao e'
direto pra `USERDEFINED` -- e' em duas etapas. 1) Classe certa nao disponivel no software ->
usa a classe mais proxima com `PredefinedType=USERDEFINED`, nomeando o tipo real no campo de
texto (ex: `IfcRailing` + `USERDEFINED` + texto "FENCE" se `FENCE` nao existir na lista do
software). 2) Nem a classe IFC mapeada existe/e' suportada -> cai pra `IfcBuildingElementProxy`
como ultimo recurso (achado em varias fichas oficiais: Tela Mosquiteira, Elemento Tensionado,
Consolo, Lastro e Berco, Elemento de Suporte e Fixacao -- todos usam `IfcBuildingElementProxy`
quando nao ha classe IFC especifica boa o suficiente pro elemento).

## Ferramentas (Autodesk BIM Interoperability Tools -- ribbon dedicada)

| Modulo | Funcao |
|---|---|
| **Classification Manager** | Atribui parametros/classificacao (incluindo `IFCExportAs`) em lote via planilha Excel (aba Parameters). Usar pra corrigir varios tipos de uma vez, sem abrir Type Properties um por um. |
| **Model Checker** + **Model Checker Configurator** | Roda/monta checksets XML de validacao -- ver template abaixo. |
| **Classification Manager, COBie Extension, Equipment Data Tool, Spatial Data Tool** | Fora do escopo de IFC export direto (COBie = facilities, Equipment = parametro de equipamento, Spatial = sincroniza Room/Area). |

### Fluxo recomendado
1. **Classification Manager** -- corrige `IFCExportAs`/categoria em lote pela planilha.
2. **Model Checker** -- roda checkset (template abaixo) pra confirmar que nao sobrou nada `USERDEFINED`/vazio/inconsistente.
3. Reexporta IFC.
4. Confere no arquivo exportado (`ifcopenshell`, `PredefinedType` do elemento deve sair limpo, nao mais o fallback pro nome do Tipo).

### Template de checkset (Model Checker) -- flag parametros IFC problematicos

```xml
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<MCSettings AllowRequired="False" Name="Validacao IFC Export" Author="Custom" Description="Checa parametros IFC antes de exportar" Image="" LastModified="0">
  <Heading ID="a1b2c3d4-0000-0000-0000-000000000001" HeadingText="Validacao IFC Export" Description="Checa preenchimento de parametros IFC" IsChecked="True">
    <Section ID="a1b2c3d4-0000-0000-0000-000000000002" SectionName="Parametros" Title="" IsChecked="True" Description="">

      <Check ID="a1b2c3d4-0000-0000-0000-000000000003"
             CheckName="IFCExportAs vazio"
             Description="Elementos sem o parametro IFCExportAs preenchido"
             FailureMessage="Elemento sem IFCExportAs definido"
             ResultCondition="FailMatchingElements"
             CheckType="Custom" IsRequired="False" IsChecked="True">
        <Filter ID="a1b2c3d4-0000-0000-0000-000000000004"
                Operator="And" Category="Parameter" Property="IFCExportAs"
                Condition="HasNoValue" Value="True"
                CaseInsensitive="False" Unit="None" UnitClass="None"
                FieldTitle="" UserDefined="False" Validation="None" />
      </Check>

      <Check ID="a1b2c3d4-0000-0000-0000-000000000005"
             CheckName="PredefinedType USERDEFINED"
             Description="Elementos com Type IFC Predefined Type = USERDEFINED"
             FailureMessage="Categoria IFC nao definida (USERDEFINED)"
             ResultCondition="FailMatchingElements"
             CheckType="Custom" IsRequired="False" IsChecked="True">
        <Filter ID="a1b2c3d4-0000-0000-0000-000000000006"
                Operator="And" Category="Parameter" Property="Type IFC Predefined Type"
                Condition="Equal" Value="USERDEFINED"
                CaseInsensitive="True" Unit="None" UnitClass="None"
                FieldTitle="" UserDefined="False" Validation="None" />
      </Check>

    </Section>
  </Heading>
</MCSettings>
```

Salva como `.xml`, importa no Model Checker Configurator (aba BIM Interoperability Tools > Configurator > Import), roda check no projeto inteiro.

## IDS (Information Delivery Specification) -- validacao padrao aberto

Alternativa ao Model Checker (que e' proprietario Autodesk): IDS e' XML
padrao buildingSMART, roda em qualquer ferramenta compatível -- inclusive
**IFC Tester**, ja embutido no Bonsai (Quality and Coordination > Quality
Control > IFC Tester), sem precisar de addin nenhum.

### Estrutura basica

```
<ids>
  <info>...</info>
  <specifications>
    <specification name="..." ifcVersion="IFC2X3">
      <applicability>
        <entity><name><simpleValue>IFCELEMENT</simpleValue></name></entity>
      </applicability>
      <requirements>
        <property cardinality="required" dataType="IFCLABEL">
          <propertySet><simpleValue>Pset_X</simpleValue></propertySet>
          <baseName><simpleValue>Y</simpleValue></baseName>
        </property>
      </requirements>
    </specification>
  </specifications>
</ids>
```

**CUIDADO com `IFCELEMENT` na applicability** -- na teoria e' classe abstrata
que devia casar com qualquer subtipo (parede, porta, laje...). Na pratica,
biblioteca `ifctester` (a que roda no Bonsai/IFC Tester) tem bug: filtro por
nome simples chama `ifc_file.by_type(nome, include_subtypes=False)`, e classe
abstrata nunca e' instanciada direto -- resultado sempre 0 elementos, `(0/0)`
mesmo o modelo tendo milhares de paredes. Confirmado testando direto:
`by_type('IFCELEMENT', include_subtypes=False)` = 0, com
`include_subtypes=True` = 20178. Pra pegar varias classes concretas de
verdade, usa `xs:restriction`/`xs:enumeration` (esse caminho SIM aciona
subtype-matching na lib):

```xml
<entity>
  <name>
    <xs:restriction base="xs:string">
      <xs:enumeration value="IFCWALL"/>
      <xs:enumeration value="IFCWALLSTANDARDCASE"/>
      <xs:enumeration value="IFCDOOR"/>
    </xs:restriction>
  </name>
</entity>
```

Repara que `IfcWall` e `IfcWallStandardCase` sao classes separadas no
IFC2X3 (a segunda e' a "concreta" que o Revit realmente exporta pra parede
comum) -- lista as duas quando quiser cobrir "toda parede".

### Erros de schema mais comuns (achados na pratica, validando de verdade)

- **`<author>` precisa ser e-mail valido** (`nome@dominio.algo` -- regex
  exige um "." depois do "@"). `jeff@vigli` falha, `jeff@vigli.com.br` passa.
- **`minOccurs`/`maxOccurs` NAO existem em `<specification>`** -- isso foi
  tentativa errada de forcar obrigatoriedade no lugar errado. Mas eles
  existem sim, so' que em **outro nivel** -- ver secao "Dois tipos de
  cardinalidade" abaixo (confirmado no manual oficial "IDS for Everyone").
- `dataType` do requirement precisa bater com o tipo IFC real da
  propriedade (`IFCPOSITIVELENGTHMEASURE` pra comprimento/altura, etc.) --
  nao e' so' cosmetico, **bate literal contra o tipo serializado no STEP,
  falha mesmo com valor presente e correto se o tipo declarado for outro**.
- **`IFCLABEL` != `IFCTEXT`, gotcha real que já derrubou validação com dado
  certo.** Shared parameter `TEXT` do Revit exporta como `IfcText` no STEP
  (`IFCTEXT`), NAO `IfcLabel`. Declarar `dataType="IFCLABEL"` numa
  propriedade que na real é `IfcText` faz o `ifctester` reprovar 100% dos
  elementos mesmo com o valor preenchido certinho -- só descobre isso
  inspecionando o STEP direto (`prop.NominalValue.is_a()` via ifcopenshell),
  o erro do relatório não indica isso, só mostra "Fail" genérico. Regra
  prática: parâmetro `TEXT` do Revit -> `IFCTEXT` no IDS, não `IFCLABEL`
  (esse último é mais pra atributo `Name`/`Tag` nativo do IFC, não pra
  propriedade custom de Pset).

### Dois tipos de cardinalidade (facil confundir)

Sao dois mecanismos diferentes, niveis diferentes:

1. **`minOccurs`/`maxOccurs` na tag `<applicability>`** -- controla se e'
   obrigatorio EXISTIR elemento que bate no filtro:
   - `minOccurs="1"` (ou omitido, default) = **Required**: pelo menos 1
     elemento tem que casar com a applicability.
   - `minOccurs="0" maxOccurs="unbounded"` = **Optional**: pode ou nao
     existir elemento, mas se existir tem que cumprir os requirements.
   - `maxOccurs="0"` = **Prohibited**: NAO pode existir elemento nenhum
     que bata nesse filtro (ex: proibir uso de `IFCPROXY` no modelo).
   ```xml
   <applicability minOccurs="0" maxOccurs="unbounded">
     <entity><name><simpleValue>IFCDOOR</simpleValue></name></entity>
   </applicability>
   ```
2. **`cardinality="required"/"optional"/"prohibited"` dentro do facet de
   requirement** (ex: `<property cardinality="required" ...>`) -- controla
   se, PARA CADA elemento ja filtrado pela applicability, aquele requisito
   especifico (propriedade/atributo/material) precisa estar preenchido.

Resumindo: `applicability` decide **quem entra na verificacao**;
`cardinality` do requirement decide **o que precisa ser verdade** pra quem
entrou. Os dois sao raramente usados juntos no mesmo `.ids` simples -- na
pratica desse projeto so' usamos o `cardinality` do requirement (todo
elemento das classes listadas precisa ter o Pset preenchido).

### FACETs disponiveis (blocos de filtro/requisito)

| FACET | Usa em applicability? | Usa em requirements? | Suporta type-inheritance? |
|---|---|---|---|
| **Entity** (`<entity>`) | Sim -- filtra por classe IFC | Raro | Sim -- `PredefinedType` casa com o Type tambem, nao so' a Instance |
| **Attribute** (`<attribute>`) | Sim -- filtra por atributo nativo (`Name`, `Description`, `ObjectType`) | Sim | Nao |
| **Property** (`<property>`) | Sim | Sim -- o mais usado nesse projeto (Pset/parametro) | Sim -- Pset de Type "vaza" pra Instance |
| **Classification** (`<classification>`) | Sim | Sim | Sim |
| **Material** (`<material>`) | Sim | Sim | Sim |
| **Part of** (`<partOf>`) | Sim -- filtra por relacao de composicao/agregacao | Sim | Sim |

`Attribute` e' o unico que NAO herda do Type pro Instance -- todos os
outros (Entity/Property/Classification/Material/Part of) consideram valor
definido no Type como valido tambem pro elemento Instance, o que bate com
como o Revit exporta Pset de Tipo (`T` no `revit_user_defined_psets.txt`).

### O que IDS NAO valida (limitacoes reais, nao tenta forcar)

- **Geometria/posicao** -- nao checa intersecao, distancia, colisao entre
  elementos (isso e' Clash Detection, outra ferramenta).
- **Valores calculados/dinamicos** -- nao soma, nao calcula area/volume
  esperado, so' compara valor ja gravado no IFC.
- **Referencia a arquivo externo** -- nao valida se um link/anexo existe.
- **Relacoes de dominio complexas** -- ex: "toda porta tem que estar numa
  parede que tem certo material" cruzando 2+ specifications nao e'
  suportado nativamente (cada specification e' isolada).

Se a necessidade for uma dessas, IDS nao e' a ferramenta certa -- documenta
o motivo em vez de tentar forcar via workaround de XML.

### Tipos de dado (`dataType`) mais usados

| dataType | Uso |
|---|---|
| `IFCLABEL` | Texto curto (nome, codigo) |
| `IFCTEXT` | Texto longo |
| `IFCIDENTIFIER` | Identificador (ex: Tag, Mark) |
| `IFCBOOLEAN` | Sim/Nao |
| `IFCINTEGER` | Numero inteiro |
| `IFCREAL` | Numero decimal generico |
| `IFCCOUNTMEASURE` | Contagem |
| `IFCLENGTHMEASURE` / `IFCPOSITIVELENGTHMEASURE` | Comprimento/altura/largura (a "positive" nao aceita negativo nem zero) |
| `IFCAREAMEASURE` | Area |
| `IFCVOLUMEMEASURE` | Volume |
| `IFCDATE` | Data |

### Regex/padrao de valor (`xs:pattern`) e faixa numerica

Alem de `simpleValue` (valor exato), o `<value>` de um requirement aceita
`xs:restriction` pra regex ou faixa:

```xml
<baseName>
  <xs:restriction base="xs:string">
    <xs:pattern value="[A-Z]{2}-[0-9]{3}"/>
  </xs:restriction>
</baseName>
```

Faixa numerica (ex: pe direito minimo/maximo):

```xml
<value>
  <xs:restriction base="xs:double">
    <xs:minInclusive value="2400"/>
    <xs:maxInclusive value="4000"/>
  </xs:restriction>
</value>
```

### Template pronto (parametro obrigatorio generico)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ids xmlns="http://standards.buildingsmart.org/IDS" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://standards.buildingsmart.org/IDS https://standards.buildingsmart.org/IDS/1.0/ids.xsd">
  <info>
    <title>TITULO</title>
    <description>DESCRICAO</description>
    <author>nome@dominio.com</author>
    <date>YYYY-MM-DD</date>
  </info>
  <specifications>
    <specification name="NOME_DO_PARAMETRO deve estar preenchido" ifcVersion="IFC2X3" instructions="Mapeamento Revit: ...">
      <applicability>
        <entity>
          <name>
            <xs:restriction base="xs:string">
              <xs:enumeration value="IFCWALL"/>
              <xs:enumeration value="IFCWALLSTANDARDCASE"/>
              <xs:enumeration value="IFCDOOR"/>
              <xs:enumeration value="IFCWINDOW"/>
              <xs:enumeration value="IFCSLAB"/>
            </xs:restriction>
          </name>
        </entity>
      </applicability>
      <requirements>
        <property cardinality="required" dataType="IFCLABEL">
          <propertySet><simpleValue>Pset_NOME</simpleValue></propertySet>
          <baseName><simpleValue>NOME_DO_PARAMETRO</simpleValue></baseName>
        </property>
      </requirements>
    </specification>
  </specifications>
</ids>
```

Repete o bloco `<specification>` uma vez por parametro obrigatorio. Lista
so' as classes IFC que realmente tem esse parametro (`xs:enumeration`) --
NAO usa `IFCELEMENT` sozinho, ver bug explicado acima.

### Validar o XML do IDS (schema valido, sem precisar de IFC)

```bash
uv run --with ifcopenshell --with ifctester python -c "
from ifctester import ids
spec = ids.open(r'caminho\para\arquivo.ids')
print('valido, specs:', [s.name for s in spec.specifications])
"
```

Se der erro, a mensagem do `xmlschema` aponta exatamente o atributo/elemento
invalido e o path na arvore XML -- confia nela, ela e' precisa.

### Rodar de verdade contra um IFC (fora do Bonsai, so' ifcopenshell)

```bash
uv run --with ifcopenshell --with ifctester python -c "
import ifcopenshell
from ifctester import ids, reporter

f = ifcopenshell.open(r'caminho\para\modelo.ifc')
spec = ids.open(r'caminho\para\arquivo.ids')
spec.validate(f)

reporter.Console(spec).report()
"
```

`(0/0)` no resultado nao e' erro -- significa que nenhum elemento do
schema/classe daquela specification foi encontrado (ex: Pset ainda nao foi
exportado do Revit). Reexporta com o Pset certo e roda de novo.

### Rodar no Bonsai (IFC Tester, sem sair do Blender)

Quality and Coordination > Quality Control > **IFC Tester** > carrega o
`.ids` > roda contra o IFC ja aberto na cena.

### Referencia oficial

Repositorio oficial buildingSMART: https://github.com/buildingSMART/IDS
- `Documentation/UserManual/` -- manual de uso
- `Documentation/ImplementersDocumentation/` -- detalhe de implementacao
- `Schema/ids.xsd` -- schema XML oficial (fonte de verdade se algo aqui
  ficar desatualizado ou surgir atributo/facet novo)

Manual completo (174 pag, PT-BR) da ACCA software -- "IDS for Everyone",
Edicao 2.0 (jul/2024): `D:\IFC\ids-for-everyone-ptb-rev-3.pdf`. Cobre a
mesma estrutura tecnica acima com mais profundidade -- Cap. 4 (FACETs
avancados e regras de type-inheritance por FACET), Cap. 7 (regex/faixa
numerica), Cap. 8 (interoperabilidade IDS<->bSDD, mapeamento
dicionario/classe/propriedade via URI), Cap. 9 (fluxo de validacao +
BCF pra reportar pendencia), Cap. 10.5 (17 exercicios resolvidos), Cap.
10.6 (exemplo real completo de mapeamento IFC pra um projeto de Kindergarten).
Ferramenta usada no manual (`usBIM.IDSeditor`/`usBIM.IDS`, ACCA) e' paga e
NAO testada nesse projeto -- serve so' como referencia de conceito, o
workflow real daqui continua sendo `ifctester`/Bonsai IFC Tester (gratis,
ja' testado, ja' documentado acima).

### Validador oficial mais rigoroso (IDS-Audit-Tool)

`ifctester` (usado acima) valida XSD + roda contra IFC. O
**IDS-Audit-Tool** oficial buildingSMART vai mais fundo: XSD + coerencia
com schema IFC real (entidade/atributo/pset existe mesmo no schema
2x3/4/4x3?) + cardinalidade + tipo de medida. .NET, CLI + lib embutivel.

- Repo: https://github.com/buildingSMART/IDS-Audit-tool
- Usar quando o `ifctester` passar mas quiser confirmar que o `.ids` bate
  100% com o schema IFC (ex: nome de Pset/propriedade que nao existe de
  verdade naquela versao do IFC, algo que so' validar XML nao pega).

## bSDD (buildingSMART Data Dictionary) -- fonte oficial de classificacao

Dicionario online buildingSMART com classificacoes/propriedades/valores
permitidos padronizados (Uniclass, Omniclass, etc.) -- equivalente oficial,
hospedado e pesquisavel, ao banco Excel usado pelo Standardized Data Tool
(secao 2 da skill `autodesk-bim-interoperability-tools`). Util pra achar o
enum/categoria certo sem depender de planilha propria.

- Repo: https://github.com/buildingSMART/bSDD
- API publica (Swagger): https://app.swaggerhub.com/apis/buildingSMART/Dictionaries/v1
- Busca web: https://search.bsdd.buildingsmart.org/
- Portal de gestao: https://manage.bsdd.buildingsmart.org/

## BCF (BIM Collaboration Format) -- coordenacao/clash, nao parametro

Escopo diferente do resto da skill: formato XML pra troca de **issues de
coordenacao** (screenshot + viewpoint 3D + comentario, vinculado a
elemento(s) IFC especifico(s)) entre disciplinas -- nao e' sobre
parametro/categoria, e' sobre comunicar pendencia/clash.

- Repo oficial: https://github.com/buildingSMART/BCF-XML
- Bonsai ja tem isso pronto, nunca exploramos a fundo: Quality and
  Coordination > **Collaboration > BCF Project**, junto com **Clash
  Detection** (Clash Sets, Clash Manager) no mesmo painel.
- TODO: passo a passo real do BCF Project no Bonsai fica pendente --
  precisa Blender conectado pra explorar a UI antes de documentar (nao
  documentar as cegas, mesma regra de sempre).

**Addin Revit correspondente:** `bSDD-Revit-plugin` (`BsddRevitPlugin.dll`)
-- conecta o Revit direto no dicionario online. Confere se ja esta instalado
antes de configurar Classification Manager/Standardized Data Tool do zero
com planilha propria -- pode ser mais rapido puxar do bSDD direto.

## IFC4.x-development -- fonte oficial do schema (avancado, uso pontual)

Repo onde buildingSMART desenvolve o schema IFC em si (nao e' ferramenta,
e' a fonte primaria): EXPRESS `.exp` por versao (IFC4, IFC4.3...) e pasta
`psd/` com definicao XML de todo Pset **oficial** (`Pset_WallCommon`,
`Pset_DoorCommon`, etc).

- Repo: https://github.com/buildingSMART/IFC4.x-development
- **Versao navegavel (site, mais pratico que clonar o repo):**
  https://ifc43-docs.standards.buildingsmart.org/ -- documentacao
  **completa** do schema: toda entidade (`IfcWall`, `IfcDoor`...), todo
  Pset/Qto oficial, todo enum (`PredefinedType` etc), atributo, regra,
  function, com hierarquia de heranca renderizada E nota de versao (desde
  quando existe / se foi depreciado -- ex: entidade so' valida a partir do
  IFC4, ou so' existe ate IFC2X3). E' a referencia primaria pra qualquer
  duvida de schema, nao so' lookup pontual de nome/enum.
- Usar pra confirmar nome/atributo/enum **oficial** antes de criar
  propriedade custom nova, checar diferenca entre versoes do schema
  (IFC2X3 vs IFC4 vs IFC4.3), ou entender heranca completa de uma
  entidade. Nao cobre `Pset_SINAPI` / `Pset_ProjetoInfo` /
  `Pset_PortaDados` (sao custom deste projeto, nao existem no schema
  oficial -- isso e' esperado, nao e' erro).
- Overlap parcial com o **IDS-Audit-Tool** (secao acima) -- aquele ja
  cruza `.ids` contra esse mesmo schema automaticamente. Usar este repo
  direto so' quando quiser ler a definicao crua, sem rodar ferramenta.

## Protocolo BIM PR -- norma oficial de contratacao publica (Parana, Brasil)

Documento oficial: "Protocolo BIM PR: Diretrizes Gerais para Contratacao de
Projetos Publicos em BIM" (SEIL/PR, 1ª edicao, 2026, 332 paginas). Fonte:
`D:\IFC\03_referencias\PROTOCOLO BIM_PR 2026.pdf`. **Verificado direto no
PDF (paginas 1-15, lidas por mim antes de delegar o resto pra agentes) --
nao vem de resumo de terceiro:** a Apresentacao (p.6) cita literalmente
"Conforme o Artigo 524 do Decreto Estadual n.º 10.086/2022, que regulamenta
a Lei Federal n.º 14.133/2021 no ambito estadual, compete a Secretaria de
Estado de Infraestrutura e Logistica (SEIL) padronizar as especificacoes
tecnicas...". Isso comprova que existe **decreto real e competencia formal
da SEIL** por tras do documento -- **nao li o decreto em si** pra confirmar
se ele torna o Protocolo obrigatorio em contrato especifico ou so' da
autoridade pra SEIL publicar a norma; tratar como "tem base regulamentar
real", nao presumir "obrigatorio em todo contrato" sem checar o decreto.
Usa a mesma base IFC/
IDS/openBIM que ja documentamos, mas formaliza uma camada de classificacao
propria por cima (EOI-PR) e um catalogo enorme de fichas tecnicas por
elemento (Apendice B, ~140 elementos). Vale como referencia sempre que
precisar de exemplo REAL e OFICIAL (nao inventado) de mapeamento IFC por
elemento de construcao.

### EOI-PR -- Estrutura de Organizacao da Informacao

Classificacao estadual, 2 niveis. O documento confirma que cada ficha tem
um campo "Mapeamento IFC" que "indica a versao e a classe... que o elemento
deve ser mapeado" -- **interpretacao pra esse projeto** (nao e' texto literal
do Protocolo): isso funciona como metadado adicional que aponta pro
`IfcExportAs`, sem substitui-lo -- na pratica, mais um campo pra conferir
consistencia junto aos 3 ja citados no topo desse arquivo.

- Formato: `PR.NN.MM` (ponto) ou `PR NN MM` (espaco). `NN` = sistema (01-30,
  2 digitos), `MM` = elemento dentro do sistema (05, 10, 15... incrementos
  de 5). Codigo terminado em `00` = so' o sistema (1º nivel).
- Cada sistema tem um elemento generico `99` pra cobrir o que nao esta
  previsto (ex: `PR 12 99 OUTRAS ESQUADRIAS`), sujeito a avaliacao da SEIL
  pra virar codigo formal depois -- **analogia minha, nao e' termo usado
  no documento**: e' o papel que o `USERDEFINED` cumpre no IFC, so' que na
  camada EOI-PR.
- 30 sistemas (1º nivel) cobrem desde Levantamento/Canteiro/Terraplenagem
  ate Edificacoes (Fechamentos, Esquadrias, Acabamentos, Cobertura) ate
  infra pesada (ferroviario, aeroportuario, portuario, tunel) -- e' uma
  norma multi-dominio, nao so' edificacao.
- EOI-PR **nao classifica por material/especificidade** -- isso fica com
  Pset/Qto. O codigo so' organiza "o que e' o elemento", nao "do que e'
  feito".

### LOIN oficial -- 4 niveis geometricos (nao confundir com LOD do mercado)

| Nivel | Nome | Definicao |
|---|---|---|
| I | Bidimensional | Geometria em 2D (linhas/poligonos) |
| II | Simplificada | 3D basico/esquematico, forma geral |
| III | Intermediaria | 3D com camadas e conexoes, detalhe suficiente pra execucao, pode omitir componente secundario |
| IV | Detalhada | 3D alta fidelidade, detalhamento pra fabricacao/montagem |

LOIN = geometrica + alfanumerica + documental. O documento comprova
explicitamente que geometria e informacao alfanumerica podem variar
**independentes** uma da outra (exemplo citado: geometria simplificada com
dado alfanumerico rico) -- independencia da informacao documental em
relacao as outras duas nao e' afirmada com a mesma clareza no texto, tratar
como provavel mas nao 100% confirmado.

### Estrutura da Ficha Tecnica (Requisitos de Informacao)

6 colunas por propriedade/quantidade exigida: **Conjunto** (Pset ou Qset) /
**Informacao** (nome do campo) / **Valor** (exemplo do que preencher) /
**Unidade** / **Tipo de dado** / **Observacoes-Nota** (orientacao de
preenchimento, ultima coluna). Mesmo padrao conceitual que usamos na
planilha `Parametros_Mapeados` (Categoria/Parametro/Status/Pset destino),
so' que oficializado com coluna de Unidade e Tipo de dado explicitas --
vale adotar essas colunas extras nas proximas planilhas de mapeamento.

Regra citada textualmente que **confirma** o gotcha `IFCLABEL`/`IFCTEXT` ja
documentado nesse arquivo: "A definicao adequada do Tipo de Dado e'
essencial para a adocao do padrao IDS, e posterior validacao automatizada
das informacoes que compoem o modelo, devendo ser rigorosamente respeitada."

### Convencao de Pset custom: "BIMPR" (equivalente oficial do nosso "Trivia")

Mesma regra buildingSMART que ja documentamos (Pset custom nao usa prefixo
`Pset_`) instanciada oficialmente, e de um jeito mais rigido que o nosso:
a Secao 5 do Protocolo determina literalmente "deve ser criado um Pset
personalizado" com nomenclatura `BIMPR` -- e' um nome **unico e generico**
pra todo Pset custom do sistema inteiro (nao um Pset por categoria de
elemento como fizemos no "Trivia", tipo `Pset_TriviaAlvenaria` separado de
`Pset_TriviaCaixilhos`). Todas as fichas do Apendice B confirmam isso na
pratica -- toda propriedade personalizada aparece rotulada `BIMPR` na
coluna Conjunto, nunca um nome diferente por elemento. Diferenca real de
estrategia a considerar: 1 Pset custom universal (padrao Parana) vs 1 Pset
custom por categoria (nossa estrategia "Trivia") -- ambos validos, cada um
com trade-off (universal = menos Pset pra gerenciar mas tudo junto; por
categoria = mais organizado mas mais Pset). Padrao real de multi-camada:
campos `Material 1`,
`Material 2` (numeracao crescente) pra elemento com mais de uma camada --
confirmado em Parede, Muro, Grade e Gradil, Porta, Janela, Claraboia
(Divisoria usa campo `Material` singular, NAO segue esse padrao -- conferido
na ficha real, nao generalizar). Se algum projeto precisar de mais de 1
material por elemento (o nosso "Trivia" hoje so' tem associacao
`IfcMaterial` unica via camada), esse e' o padrao oficial pra seguir.

### Tabela de mapeamento IFC oficial por elemento -- Arquitetura/Edificacao

Extraida do Apendice B (fichas tecnicas reais). Uso: confirmar/comparar
contra mapeamento proprio antes de assumir uma classe por conta.

| Elemento (EOI-PR) | Classe/PredefinedType IFC oficial |
|---|---|
| Parede (PR.11.05) | `IfcWall` |
| Divisoria (PR.11.10) | `IfcWall.PARTITIONING` |
| Grade e Gradil (PR.11.15) | `IfcRailing.FENCE` |
| Muro (PR.11.20) | `IfcWall` |
| Parede Estrutural (PR.08.45) | `IfcWall.SOLIDWALL` |
| Porta (PR.12.05) | `IfcDoor` |
| Janela (PR.12.10) | `IfcWindow` |
| Portao (PR.12.15) | `IfcDoor.GATE` |
| Pele de Vidro (PR.12.20) | `IfcCurtainWall` |
| Claraboia (PR.12.25) | `IfcWindow.LIGHTDOME` (horizontal) / `.SKYLIGHT` (inclinada) |
| Brise (PR.12.30) | `IfcShadingDevice` |
| Alcapao (PR.12.35) | `IfcDoor.TRAPDOOR` |
| Veneziana Fixa (PR.12.40) | `IfcWindow` |
| Tela Mosquiteira (PR.12.45) | `IfcBuildingElementProxy` |
| Contrapiso (PR.13.05) | `IfcCovering.TOPPING` |
| Revestimento de Piso (PR.13.10) | `IfcCovering.FLOORING` |
| Soleira e Pingadeira (PR.13.15) | `IfcCovering.FLOORING`/`.COPING` |
| Revestimento de Parede (PR.13.20) | `IfcCovering.CLADDING` |
| Forro (PR.13.25) | `IfcCovering.CEILING` |
| Acabamento de Teto (PR.13.30) | `IfcCovering.CEILING` (sem estrutura suspensa, diferente de Forro) |
| Rodateto (PR.13.35) | `IfcCovering.MOLDING` |
| Rodameio (PR.13.40) | `IfcCovering` (sem PredefinedType especifico) |
| Rodape (PR.13.45) | `IfcCovering.SKIRTINGBOARD` |
| **Impermeabilizacao (PR.13.50)** | **`IfcCovering.MEMBRANE`** |
| Telha (PR.14.05) | `IfcCovering.ROOFING` |
| Rufo (PR.14.10) | `IfcDiscreteAccessory.FLASHING` |
| Cumeeira (PR.14.20) | `IfcCovering.ROOFING` |
| Toldo (PR.14.25) | `IfcShadingDevice.AWNING` |
| Estrutura da Cobertura (PR.14.30) | `IfcMember` |
| Espaco (PR.15.05) | `IfcSpace` |
| Escada (PR.08.55) | `IfcStair` (`STRAIGHT_RUN_STAIR`, `HALF_TURN_STAIR`, `QUARTER_TURN_STAIR`, `SPIRAL_STAIR`) |
| Rampa (PR.08.60) | `IfcRamp` |
| **Guarda-Corpo e Corrimao (PR.22.05)** | `IfcRailing` com subtipos `.GUARDRAIL` (guarda-corpo) / `.HANDRAIL` (corrimao) -- usa **Pset oficial nativo** `Pset_RailingCommon.Height` + `Qto_RailingBaseQuantities.Length`, sem Pset custom pra esses 2 campos |
| Escada Marinheiro (PR.22.15) | `IfcStair.LADDER` + `Pset_StairCommon` (Status, `NumberOfTreads`) |
| Loucas (PR.20.05) | `IfcSanitaryTerminal` com subtipos `.BIDET`/`.BATH`/`.URINAL`/`.TOILETPAN`/`.SINK` -- **atencao**: diferente do `IfcFlowTerminal` que usamos no nosso `Pset_TriviaSanitarios`, conferir se vale ajustar |
| Metais e Acabamentos (PR.20.10) | `IfcSanitaryTerminal` (generico, sem PredefinedType especifico) |
| Acessorios (PR.20.15) | `IfcFurnishingElement` |

**Achado importante -- corrige suposicao errada feita nessa mesma sessao:**
tinhamos especulado que Impermeabilizacao sairia como **camada de material**
dentro do Slab/Roof (sem elemento IFC proprio), por nao achar exemplo real
no modelo Vigli. O Protocolo BIM PR oficial documenta o contrario:
Impermeabilizacao tem **ficha tecnica propria**, mapeada pra
`IfcCovering.MEMBRANE` (Material, Espessura, `Qto_CoveringBaseQuantities.NetArea`,
`Pset_CoveringCommon.Status`) -- mesmo padrao dos outros revestimentos.
**Interpretacao/recomendacao pra esse projeto** (o Protocolo nao diz
explicitamente "modele como objeto, nunca como camada" -- e' inferencia
a partir do fato de ter ficha tecnica dedicada, nao proibicao literal):
se for seguir o padrao oficial de perto, vale considerar modelar
Impermeabilizacao como objeto `IfcCovering` proprio, nao so' uma camada
escondida dentro da parede/laje/telhado -- mas confirmar com quem modela
antes de forcar a mudanca.

**Confirma decisao ja tomada:** Guarda-Corpo oficial (ficha PR.22.05,
verificada campo a campo) usa **Pset nativo**
(`Pset_RailingCommon.Height`/`Qto_RailingBaseQuantities.Length`),
reforcando a estrategia ja fechada nesse projeto de "prefere Pset/Qto
oficial sempre que existir, custom so' pro resto".

### Pset reutilizavel pra vidro (Porta/Janela/Claraboia)

Porta (quando material 2 = vidro), Janela e Claraboia usam o mesmo bloco
oficial (**nao generalizar pra "todo elemento com vidro"** -- Pele de
Vidro, por exemplo, usa campos custom proprios `Tipo de vidro`/`Cor do
vidro`/`Espessura do vidro`, nao esse bloco):

- `Pset_DoorWindowGlazingType`: `GlassLayers` (IfcCountMeasure),
  `GlassThickness1` (IfcPositiveLengthMeasure), `GlassColour` (enum:
  Verde/Incolor/Fume/Reflexivo), `IsTempered`/`IsLaminated`/`IsCoated`
  (IfcBoolean cada).
- Tipo de abertura: `Pset_DoorPanelProperties.PanelOperation` (porta --
  enum: DOUBLE_ACTING, FIXEDPANEL, FOLDING, REVOLVING, ROLLINGUP, SLIDING,
  SWINGING, OTHER) ou `Pset_WindowPanelProperties.OperationType` (janela --
  enum bem maior: BOTTOMHUNG, FIXEDCASEMENT, PIVOTHORIZONTAL, PIVOTVERTICAL,
  SLIDINGHORIZONTAL/VERTICAL, TILTANDTURN*, TOPHUNG, etc).

### Data Types adicionais (complementa a tabela ja existente na secao IDS)

| dataType oficial | Uso |
|---|---|
| `IfcCompoundPlaneAngleMeasure` | Coordenada geografica (RefLatitude/RefLongitude de IfcSite) |
| `IfcCountMeasure` | Contagem usada como **atributo de projeto** (fora de Qset) -- ex: numero de faixas de rodovia. Diferente de `IfcQuantityCount`, que so' existe **dentro** de um Qset |
| `IfcIdentifier` | Codigo/ID unico (material, norma) -- ja documentado, reforcado aqui |

### Atributos oficiais de IfcProject/IfcSite/IfcBuilding (Quadros 8-10)

Referencia pronta pra quando for montar Dados Basicos de projeto novo --
overlap direto com o que fizemos em `Pset_TriviaDadosBasicos`:

- **IfcProject**: `Name` (atributo nativo), `Tipo de projeto` (Pset custom,
  ex: Reforma), `Pset_ProjectCommon.ProjectInvestmentEstimate`
  (IfcCostValue, R$), `Pset_ProjectCommon.FundingSource` (IfcLabel).
- **IfcSite**: `Name`, `RefLatitude`/`RefLongitude` (atributo nativo,
  `IfcCompoundPlaneAngleMeasure`), `RefElevation` (`IfcLengthMeasure`),
  `Pset_Address.AddressLines`/`Town`/`PostalCode`/`Region`,
  `Pset_SiteCommon.TotalArea` (`IfcAreaMeasure`).
- **IfcBuilding**: `Name`, `Fase` (Pset custom), `Pset_BuildingCommon.OccupancyType`,
  `Pset_BuildingCommon.YearOfConstruction`/`YearOfLastRefurbishment`.

### O que esse resumo NAO cobre ainda

So' li Secao 5 (conceitos/padroes) + Apendice B inteiro (fichas tecnicas,
todas as ~140, via agentes paralelos). Nao li Secoes 1-4 (contexto/gestao
ISO 19650) nem Apendice A (preenchimento do BEP) -- se precisar de BEP ou
do processo de gestao formal ISO 19650 adaptado a administracao publica,
essas partes ainda nao foram extraidas.

## ISO 19650 -- cadeia de governanca da informacao

Vocabulario formal que faltava nessa skill (so' tinhamos IDS documentado
isolado, sem o contexto de onde ele se encaixa). Fonte: guia visual
interativo `github.com/jeffersonbim/guia-bim-19650` (repo proprio do
usuario, buildingSMART certificado -- dado embutido em `index.html`,
arrays `DOCS[]`/`EXAMPLES{}`). So' extraida a **cadeia central** (~10
documentos de ISO 19650-1/2) -- o repo tem tambem detalhamento processual
completo de ISO 19650-2 §5.1-5.8 (27 processos) e Partes 3/4/5 inteiras
(operacao de ativo, troca de informacao, seguranca), nao extraidas ainda
por serem mais operacional/gestao do que parametrizacao Revit/IFC.

### Cadeia sintese

```
OIR ──→ AIR ──→ EIR ──→ BEP ──→ IDS ──→ MIDP ──→ AIM ──→ PIR
 ↑                ↑                                        ↓
Permanente    Contratual                              Realimenta OIR
```

Comeca nos requisitos organizacionais (OIR, permanente, nao pertence a
projeto especifico), passa pelos requisitos contratuais (EIR, base
contratual do projeto), estrutura a producao (BEP + IDS + TIDP/MIDP) e
termina no modelo operacional do ativo (AIM) -- avaliado pelo PIR/
encerramento, que realimenta o OIR do proximo empreendimento.

### Os 10 documentos centrais

| Sigla | Nome | Norma | O que resolve (decisao) |
|---|---|---|---|
| **OIR** | Organizational Information Requirements | ISO 19650-1 §5.2 / -3 | Que informacao a organizacao precisa pra gerir ativos na vida util toda? Documento estrategico permanente, nao e' de projeto. |
| **AIR** | Asset Information Requirements | ISO 19650-1 §5.3 / -3 | Que dados de FM (facilities management) esse ativo especifico precisa pra operacao/manutencao pos-entrega? Ponte entre OIR e EIR. |
| **EIR** | Exchange Information Requirements | ISO 19650-1 §3.3.6 / -2 §5.1.2 | O que, em qual formato, LOD, prazo e criterio a equipe contratada deve entregar? **Base contratual** -- sem EIR nao da pra avaliar conformidade. |
| **BEP** | BIM Execution Plan | ISO 19650-2 §5.3.2 e §5.4.1 | Resposta formal da equipe contratada ao EIR. 2 camadas: **pre-contratual** (proposta tecnica, avaliada antes de assinar) e **definitivo** (guia operacional, aprovado antes de produzir). |
| **IDS** | Information Delivery Specification | ISO 21597 / buildingSMART | Como verificar automatico se a entrega atende o EIR? **Nao substitui o EIR, formaliza os criterios dele em regra computacional verificavel.** |
| **TIDP** | Task Information Delivery Plan | ISO 19650-2 §5.4.4 | Cronograma de entrega de informacao de **1 disciplina** especifica. Cada parte contratada (AP) faz o proprio. |
| **MIDP** | Master Information Delivery Plan | ISO 19650-2 §5.4.5 | Consolidacao de todos os TIDP num cronograma mestre unico -- mantido pelo LAP (lider) durante a execucao inteira. |
| **AIM** | Asset Information Model | ISO 19650-1 §5.6 / -3 | Modelo final entregue pra operacao, validado contra o AIR original. LOD 400 (as-built), destino CAFM/CMMS/BMS. |
| **PIR** | Project Information Requirements | ISO 19650-1 §3.3.5 / §5.4 | Que perguntas o contratante precisa responder em cada ponto-chave de decisao do empreendimento? Delimita o EIR. |
| **ENC** | Encerramento (Licoes Aprendidas) | ISO 19650-2 §5.8 | Pos-entrega do AIM: arquiva o PIM no CDE + registra licoes -- **realimenta o OIR** do proximo empreendimento. |

### Nota importante sobre IDS (esclarece posicao na cadeia)

Achado direto do repo, vale reforcar aqui porque essa skill documenta IDS
tecnicamente mas nunca tinha explicado onde ele se encaixa na governanca:
"O IDS e' um instrumento de verificacao, nao de origem dos requisitos. A
origem esta no EIR (contratual) → AIR (FM) → OIR (estrategico). O IDS
traduz esses requisitos em regras automaticas." Na pratica: quando for
criar um `.ids`, os campos obrigatorios que ele valida deveriam vir de um
EIR/requisito ja definido -- o `.ids` formaliza uma exigencia que ja
deveria existir em contrato, nao e' ele que "inventa" o requisito.

### Onde acessar

- Repo: `github.com/jeffersonbim/guia-bim-19650`
- Guia interativo (site): `jeffersonbim.github.io/guia-bim-19650/`
- Formato: single-file HTML (`index.html`, ~6800 linhas), zero dependencia
  de servidor -- Kanban por fase, Gantt com predecessoras reais, drawer
  normativo com fluxos e diagramas da norma, exemplos clicaveis por
  documento.

## Revit API direto via `send_code_to_revit` (MCP `revit-mcp`)

Pra confirmar de verdade como um parametro esta vinculado no Revit (Instance
vs Type, Shared vs Project Parameter) antes de mexer no
`revit_user_defined_psets.txt` -- mais confiavel que assumir.

- Referencia oficial da API (C#), versao bate com addin instalado
  (Revit 2024 / build R24): https://www.revitapidocs.com/2024/
- **Gotcha real:** o template do `send_code_to_revit` expoe o documento
  como parametro `document` (minusculo), NAO `doc`. `var x = doc.Title`
  falha ("Document e' um tipo, nao contexto valido"); `document.Title`
  funciona.
- Exemplo pra checar binding de um parametro antes de editar o mapeamento:
  ```csharp
  var def = document.ParameterBindings;
  var it = def.ForwardIterator();
  it.Reset();
  while (it.MoveNext())
  {
      var d = it.Key as Autodesk.Revit.DB.Definition;
      if (d != null && d.Name == "Fase do Projeto")
      {
          var binding = it.Current as Autodesk.Revit.DB.ElementBinding;
          return binding is Autodesk.Revit.DB.InstanceBinding ? "Instance" : "Type";
      }
  }
  return "nao encontrado";
  ```
- Resultado desse tipo de query e' o que decide `T` ou `I` na segunda
  coluna do `.txt` (ver secao do `revit_user_defined_psets.txt` acima) --
  errar isso faz o Pset sair vazio no IFC sem erro nenhum no export.

## Gotchas reais de producao (mapeamento multi-categoria, validados em projeto)

Achados trabalhando um mapeamento completo de parametros por disciplina
(shared parameter unico + Pset custom por categoria) -- cada um custou uma
rodada real de debug, nao e' teoria.

### Exportador Revit pula propriedade vazia -- o Pset inteiro some

Se **todas** as propriedades de um bloco `PropertySet:` estao vazias pra um
elemento, o Pset inteiro nao aparece no IFC exportado -- nao e' bug do
mapeamento nem do binding, e' comportamento nativo do exportador Revit
(so serializa propriedade com valor). Isso quebra a premissa de "validar
so' presenca, nao precisa estar preenchido": na pratica, presenca SEM
nenhum valor de teste nunca aparece no IFC. Pra validar de verdade que um
mapeamento funciona ponta a ponta, precisa preencher **pelo menos 1 valor
de teste** em pelo menos 1 Type/Instance de cada categoria antes de
exportar -- confirma o pipeline, depois reverte/ajusta.

### Categoria Revit != classe IFC exportada (nos dois sentidos)

O filtro do `revit_user_defined_psets.txt` opera na **classe IFC final**
(depois de qualquer override de `IFCExportAs`), nao na categoria do Revit.
Isso da dois tipos de problema:

1. **Mesma categoria Revit, classes IFC diferentes**: elemento modelado
   como "Curtain Wall" (categoria Walls no Revit) pode exportar como
   `IfcCurtainWall`, enquanto Alvenaria normal (mesma categoria Walls)
   exporta `IfcWall`/`IfcWallStandardCase`. Um guarda-corpo modelado como
   cortina (tecnica comum pra contornar limitacao geometrica da ferramenta
   nativa Railing) **nao** casa com filtro `IfcRailing`. Solucao: repetir
   o mesmo nome de Pset em blocos `PropertySet:` separados, um filtro por
   classe (`IfcRailing` + `IfcCurtainWall` apontando pro mesmo
   `Pset_TriviaGuardaCorpo`) -- e' recurso nativo do formato, nao precisa
   de Parameter Mapping Table nem nada especial.
2. **Categorias diferentes de matriz, mesma classe IFC final**: o inverso
   -- revestimento vertical, horizontal e paisagismo (grama/piso externo)
   podem todos exportar como `IfcCovering` sem diferenca de
   `PredefinedType` no filtro do mapeamento (esse arquivo so filtra por
   classe, nao por `PredefinedType`). Nao da pra separar 3 Pset diferentes
   só com esse mecanismo -- ou junta num Pset so, ou resolve depois via
   pos-processamento no IFC (ifcopenshell, olhando `PredefinedType`).

### Categorias internas do Revit "escondidas" (corrimao/lance de escada)

Escada por componente (Stair by Component, padrao desde ~Revit 2015) gera
sub-elementos com **categoria propria**, diferente da categoria "Stairs"
visivel:
- Corrimao de escada = `OST_StairsRailing` (categoria interna diferente de
  `OST_Railings`, que e' pro guarda-corpo avulso/varanda -- os dois
  aparecem como "Railings" na interface, mas sao enums diferentes).
- Lance/degrau = `OST_StairsRuns` (categoria "Runs").
- Patamar = `OST_StairsLandings` (categoria "Landings").

Um shared parameter vinculado via "All categories" no Project Parameters
**pode nao pegar essas 3** automaticamente (categoria oculta/nao lista
por padrao dependendo da versao) -- vincula explicito se usar Type
binding em elemento de escada, ou o valor simplesmente nao aparece nesses
sub-componentes mesmo com o Type "pai" (Stairs) preenchido certo.

### `Category.GetCategory()` retorna `null` se a categoria esta vazia

Via API (`send_code_to_revit`), `Autodesk.Revit.DB.Category.GetCategory(document, BuiltInCategory.OST_X)`
pode retornar `null` se nenhum elemento/familia dessa categoria foi
carregado no projeto ainda -- mesmo a categoria sendo valida. Sempre
checa null antes de inserir num `CategorySet`, senao a chamada de binding
inteira quebra com erro generico ("Exception has been thrown by the
target of an invocation"), sem indicar qual categoria foi o problema.

### Config de IFC Export Setup pode salvar no item errado da lista

No dialogo "Modify Setup" do Revit, a lista de setups fica na esquerda e
as abas (General/Property Sets/etc) editam **o item destacado**. Se
clicar entre abas sem confirmar qual setup ta selecionado, e facil editar
a aba Property Sets com um setup errado destacado (ex: editar
"Engetrens_Fase1" mas o item ainda destacado e' outro setup da lista
"IFC 2x3 GSA Concept Design..."). Sintoma: export sai sem nenhum Pset
custom, mesmo com o `.txt` certo aparentemente configurado -- porque foi
salvo no setup errado. Sempre clica direto em cima do nome do setup antes
de mexer em qualquer aba.

### Pset oficial de Material por tipo (nao existe generico universal)

buildingSMART cobre propriedade de engenharia de material (resistencia,
modulo elastico) via Pset **especifico por tipo de material**, nao um
Pset generico: `Pset_MaterialConcrete` (CompressiveStrength),
`Pset_MaterialSteel`, `Pset_MaterialWood` (StrengthGrade),
`Pset_MaterialHygroscopic` (VaporPermeability, resistencia a umidade),
`Pset_MaterialMechanical` (YoungModulus/ShearModulus -- generico mas so'
propriedade elastica, nao "resistencia" como rating simples). Esses ficam
vinculados na categoria especial **"Materials"** do Revit (Manage >
Shared Parameters > categoria Materials), nao no Tipo/Instance do
elemento -- mecanismo diferente do resto. Se o material do elemento nao
se encaixa em nenhuma dessas (ex: ceramica/porcelanato de piso), **nao
existe Pset oficial** -- e lacuna real do schema, nao falta de busca; Pset
custom no elemento e' a saida legitima nesse caso.

Fonte completa dos nomes de propriedade oficiais Revit-IFC (shared
parameter file gerado pela comunidade, nomeado `Ifc<Pset>.<Propriedade>`
-- Revit reconhece esse padrao de nome automaticamente e roteia pro Pset
oficial certo, sem precisar de `revit_user_defined_psets.txt` nem
Parameter Mapping Table): arquivo `IFC Shared Parameters-RevitIFCBuiltIn_ALL.txt`
(instance) / `...-Type_ALL.txt` (type), grep por `Pset_Material`,
`Strength`, `Moisture` etc pra achar candidato antes de assumir que
precisa criar parametro custom.

## Como confirmar que corrigiu (via ifcopenshell, fora do Revit)

```python
import ifcopenshell.util.element as elutil
predefined = elutil.get_predefined_type(elemento)
# Se retornar nome do Tipo (texto longo) em vez de enum curto (DOOR, WINDOW...)
# = ainda ta USERDEFINED sem categoria real, precisa corrigir no Revit.
```

Compara `Qto_XxxBaseQuantities.GrossXxx` vs `NetXxx` do mesmo elemento -- se forem identicos (diferenca so' ruido de ponto flutuante ~1e-15), o exportador Revit nao descontou vao/abertura, e' bug de exportacao, nao do processo de analise.

## Prompts de auditoria (adaptados do ebook "120 Prompts BIM" -- Agostinho Couto/MU-Gen)

Prompts uteis pra rodar em cima do CSV/xlsx ja exportado do Bonsai (`ifc_consolidado_*.csv`) ou dos Psets do projeto (`Pset_SINAPI`, `Pset_ProjetoInfo.FaseDoProjeto`, `Pset_ProjetoInfo.ObjetivoSetor`, `Pset_ProjetoInfo.PeDireito`). Nao substituem o `.ids`/`ifctester` (validacao formal) -- servem pra relatorio legivel por humano/cliente a partir do mesmo dado.

### Auditoria Informacional Completa

```
Com base neste extrato/lista/IFC [COLAR CSV EXPORTADO DO BONSAI], gera uma
Auditoria Informacional Completa:
I. Parametros obrigatorios vs. preenchidos (Pset_SINAPI.SINAPI,
   Pset_ProjetoInfo.FaseDoProjeto, Pset_ProjetoInfo.ObjetivoSetor,
   Pset_ProjetoInfo.PeDireito) -- tabela por disciplina, % conformidade
II. Inconsistencias detectadas (formatacao, valores fora do intervalo)
III. Anomalias (elementos sem parametro, campos vazios criticos, duplicados)
IV. Impacto no processo BIM (coordenacao, IFC, QTO, LOIN)
V. Prioridades (Alta/Media/Baixa)
VI. Resumo executivo (<10 linhas)
```

### Validacao LOIN (Previsto vs Real)

```
Compara este LOIN [4 parametros obrigatorios do projeto] com estes dados
de modelo [COLAR CSV/IFC] e gera tabela "Previsto vs. Atual", elementos
nao conformes, parametros em falta, lista de correcoes urgentes.
```

Complementa o `.ids` -- roda o `.ids` primeiro (fonte de verdade, pass/fail
formal), depois usa este prompt pra transformar o resultado em relatorio
legivel pro cliente/responsavel Revit.

### RFI pra pendencia de parametro

```
Redige um RFI sobre [PARAMETRO] nao preenchido em [N] elementos da
categoria [X], incluindo: contexto, elementos/GlobalId envolvidos, impacto
(bloqueia validacao IDS / exportacao), prazo desejado, responsavel.
```

Usar quando o `.ids` reportar `(N/M) FAIL` com N alto -- formaliza a
pendencia em vez de só reportar o numero.

Fonte completa dos 120 prompts (7 modulos: Gestao de Projetos, Documentacao
Tecnica, Coordenacao BIM, QA/QC Digital, Lean BIM, Visualizacao,
Integracao/Automacao): `D:\IFC\Ebook-IA BIM.pdf`.
