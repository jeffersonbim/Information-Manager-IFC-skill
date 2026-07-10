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

`IFCELEMENT` na applicability casa com qualquer subtipo (paredes, portas,
lajes...) -- nao precisa listar classe por classe se a regra for geral.

### Erros de schema mais comuns (achados na pratica, validando de verdade)

- **`<author>` precisa ser e-mail valido** (`nome@dominio.algo` -- regex
  exige um "." depois do "@"). `jeff@vigli` falha, `jeff@vigli.com.br` passa.
- **`minOccurs`/`maxOccurs` NAO existem em `<specification>`** -- isso foi
  tentativa errada de forcar obrigatoriedade no lugar errado. O jeito certo
  e' o atributo `cardinality="required"` **dentro do facet de requirement**
  (ex: `<property cardinality="required" ...>`), nao na tag specification.
- `dataType` do requirement precisa bater com o tipo IFC real da
  propriedade (`IFCLABEL` pra texto, `IFCPOSITIVELENGTHMEASURE` pra
  comprimento/altura, etc.) -- nao e' so' cosmetico, usado na validacao.

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
    <specification name="NOME_DO_PARAMETRO deve estar preenchido" ifcVersion="IFC2X3">
      <applicability>
        <entity>
          <name><simpleValue>IFCELEMENT</simpleValue></name>
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

Repete o bloco `<specification>` uma vez por parametro obrigatorio.

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

## Como confirmar que corrigiu (via ifcopenshell, fora do Revit)

```python
import ifcopenshell.util.element as elutil
predefined = elutil.get_predefined_type(elemento)
# Se retornar nome do Tipo (texto longo) em vez de enum curto (DOOR, WINDOW...)
# = ainda ta USERDEFINED sem categoria real, precisa corrigir no Revit.
```

Compara `Qto_XxxBaseQuantities.GrossXxx` vs `NetXxx` do mesmo elemento -- se forem identicos (diferenca so' ruido de ponto flutuante ~1e-15), o exportador Revit nao descontou vao/abertura, e' bug de exportacao, nao do processo de analise.
