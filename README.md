# IFC Revit Parametrizacao — Skill

Skill do Claude Code (`SKILL.md`) pra parametrizar corretamente Revit→IFC
(`IfcExportAs`, `Type IFC Predefined Type`) e criar/validar arquivos **IDS**
(Information Delivery Specification, buildingSMART) exigindo parametros
obrigatorios no modelo.

> ⚠️ Status: privado enquanto a skill está em teste.

## O que cobre

- Diagnostico e formato correto do `IfcExportAs` (evita erro tipo material-como-categoria, `USERDEFINED` evitavel, classe IFC4 num projeto IFC2x3)
- Tabela de enums validos por classe (IFC2x3)
- Template de checkset Model Checker (XML)
- **IDS**: estrutura, erros de schema reais encontrados na pratica, template pronto, como validar (`ifctester`) e rodar contra IFC de verdade
- Referencias oficiais buildingSMART: IDS, bSDD (dicionario de classificacao), BCF (coordenacao/clash), IDS-Audit-Tool (validador mais rigoroso)

## Skill irmã

`autodesk-bim-interoperability-tools` — cobre as ferramentas Autodesk
(Shared Parameters Tool, Standardized Data Tool, Model Checker Configurator,
COBie Extension, Room & Area Sync) que geram/corrigem os parametros que
essa skill valida.

## Origem

Nasceu de uma sessão de debug real corrigindo exportação IFC de um modelo
Revit real (bugs encontrados: `IfcExportAs` com material em vez de
categoria, `USERDEFINED` evitável, filtro com vírgula quebrando no Bonsai,
campos `.id` crashando query, `Gross`=`Net` em quantidade de parede).
