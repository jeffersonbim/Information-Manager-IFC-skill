# Conhecimento 2 — IDS

## Objetivo

Traduzir requisitos de informação já aprovados em regras IDS 1.0 e validar entregas IFC com cobertura rastreável.

## Processo

1. Identificar a origem do requisito, responsável, marco, schema e critério de aceitação.
2. Definir `applicability` com classes/facets suficientes para cobrir a população pretendida.
3. Definir requirements, cardinalidade, tipo de dado, unidade e restrições.
4. Validar XML contra o XSD oficial.
5. Executar o IDS contra fixtures e contra uma cópia do IFC real.
6. Reportar população aplicável, aprovados, reprovados e não avaliados por `GlobalId`.

## Regras

- IDS é padrão buildingSMART; ISO 21597 trata ICDD.
- IDS operacionaliza requisitos, mas não substitui OIR/AIR/PIR/requisitos de troca/BEP.
- `0/0` é `warning` de cobertura até que a ausência de aplicáveis seja justificada.
- Não generalizar comportamento de uma versão do IfcTester. Registrar e fixar versão.
- Não assumir `TEXT → IFCTEXT` ou outro tipo sem inspecionar o valor IFC/mapeamento.
- Não confundir cardinalidade da applicability com cardinalidade do requirement.
- IDS não valida geometria, clash, cálculo agregado ou existência de arquivo externo.

## Gate de aceitação

- XSD válido.
- Entidades/facets compatíveis com o schema IFC.
- Teste positivo e teste negativo passam conforme esperado.
- Cobertura explicada; nenhum `0/0` silencioso.
- Resultado reproduzível com versões registradas.

## Fontes primárias

- IDS 1.0: https://github.com/buildingSMART/IDS
- Visão técnica: https://technical.buildingsmart.org/projects/information-delivery-specification-ids/
- IfcTester: https://github.com/IfcOpenShell/IfcOpenShell
