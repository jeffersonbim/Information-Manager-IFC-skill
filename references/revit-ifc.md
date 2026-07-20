# Conhecimento 1 — Revit–IFC

## Objetivo

Diagnosticar e orientar exportações IFC sem misturar parâmetros legados, schema ou versão do exportador.

## Entrada mínima

- Versão do Revit e do add-in IFC.
- Schema/MVD de destino: IFC2x3, IFC4 ou IFC4.3 e finalidade da troca.
- Categoria Revit, família/tipo e resultado IFC observado.
- Configuração de exportação e parâmetros de instância/tipo relevantes.

## Processo

1. Confirmar a versão antes de indicar parâmetros.
2. Em Revit 2023+, priorizar `Export to IFC As`/`IFC Predefined Type` e equivalentes de tipo. Tratar `IFCExportAs`/`IFCExportType` como legado, salvo evidência de fluxo específico.
3. Validar classe e enum no schema exato. Não transportar enum IFC4/4.3 para IFC2x3.
4. Diferenciar classe da ocorrência e classe do tipo.
5. Exportar uma cópia de teste e verificar o IFC resultante por `GlobalId`, classe, `PredefinedType`, tipo e Psets.
6. Registrar versão, setup e evidência do antes/depois.

## Regras

- Material não é `PredefinedType`.
- `USERDEFINED` exige `ObjectType` significativo; `NOTDEFINED` não substitui decisão de classificação.
- `IfcBuildingElementProxy` é último recurso, não fallback automático.
- Psets vazios podem não ser serializados; testar pelo menos um valor controlado sem contaminar a entrega.
- Não presumir que categoria Revit equivale à classe IFC final.
- Não pós-processar o IFC original: trabalhar em cópia, registrar checksum, ferramenta e transformação.

## Evidência de conclusão

- IFC abre sem erro.
- Classe e enum existem no schema declarado.
- Ocorrência e tipo estão coerentes.
- Propriedades esperadas aparecem no contêiner correto.
- Relatório contém versões, `GlobalId` de amostra e limitações.

## Fontes primárias

- Autodesk Support — parâmetros novos e legados: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-map-old-IfcExportAs-and-IfcExportType-parameter-values-to-new-Export-to-IFC-As-and-IFC-Predefined-Type-parameters.html
- Autodesk Support — mapping table: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/REVIT-How-to-use-the-IFC-parameter-mapping-table.html
- IFC 4.3: https://ifc43-docs.standards.buildingsmart.org/
