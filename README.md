# Information Manager IFC Skill

Skill do [Claude Code](https://claude.com/claude-code) especializada em parametrização IFC no Revit e validação de requisitos de informação via IDS (Information Delivery Specification, buildingSMART).

## Objetivo

Reduzir o tempo entre "exportei IFC do Revit" e "o modelo tem os parâmetros certos, na categoria certa, validáveis por padrão aberto" — sem depender de tentativa e erro repetido a cada exportação.

## Conteúdo da skill

| Área | O que cobre |
|---|---|
| Diagnóstico de exportação | Checklist para validar `Export Type to IFC As`, `Type IFC Predefined Type` e `IFCExportAs` antes de exportar; erros reais já identificados (material usado como categoria, `USERDEFINED` evitável, classe IFC4 num projeto IFC2x3) |
| Enums IFC2x3 | Tabela de valores válidos de `PredefinedType` por classe mais comum |
| Model Checker | Template de checkset XML pronto para adaptar |
| IDS | Estrutura de um `.ids`, os dois erros de schema mais comuns na prática (formato de e-mail do `<author>`, cardinalidade não vai em `<specification>`), template mínimo reutilizável, comandos de validação (`ifctester`) e de execução contra um IFC real |
| Padrões abertos buildingSMART | Referência cruzada a IDS, bSDD (dicionário de classificação), BCF (coordenação/clash) e IDS-Audit-Tool (validador oficial mais rigoroso que o `ifctester`) |
| Auditoria via IA | Prompts de auditoria informacional, validação LOIN e RFI de pendência de parâmetro, adaptados do ebook *120 Prompts BIM* (Agostinho Couto / MU-Gen) para rodar sobre exports reais do Bonsai |
| Verificação programática | Snippets `ifcopenshell` para confirmar correções fora do Revit (PredefinedType com fallback de tipo, Gross vs Net) |

## Quando usar

- Configurar parâmetros IFC de famílias/tipos no Revit antes de exportar
- Revisar categoria/`PredefinedType` de um IFC já exportado
- Criar ou validar um arquivo `.ids`
- Usar Classification Manager, Model Checker ou IFC Tester (Bonsai)

## Instalação

```bash
git clone https://github.com/jeffersonbim/Information-Manager-IFC-skill.git ~/.claude/skills/ifc-especialista
```

O Claude Code carrega a skill automaticamente a partir de `~/.claude/skills/`.

## Skill relacionada

[`autodesk-bim-interoperability-tools`](https://github.com/jeffersonbim/autodesk-bim-interoperability-tools-skill) — cobre o lado Autodesk (Shared Parameters Tool, Standardized Data Tool, Model Checker Configurator, COBie Extension, Room & Area Sync) que gera os parâmetros que esta skill valida. Esta skill cobre o lado ifcopenshell/Blender/buildingSMART do mesmo fluxo.

## Origem

Construída a partir de uma sessão real de debug de exportação IFC de um modelo Revit em produção. Cada seção documenta um bug ou erro de schema efetivamente encontrado e corrigido — não é teoria, é o registro do que quebrou e de como foi resolvido.

## Licença

[MIT](LICENSE) — use, modifique e redistribua livremente, inclusive em projetos comerciais.
