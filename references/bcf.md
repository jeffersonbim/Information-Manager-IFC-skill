# Conhecimento 5 — BCF

## Objetivo

Registrar, distribuir e encerrar issues de coordenação com contexto BIM rastreável.

## Escopo

BCF não é apenas clash nem apenas XML. Declarar se o fluxo usa BCF-XML ou BCF API/OpenCDE e qual versão é suportada.

## Processo

1. Criar issue com título objetivo, descrição, tipo, prioridade e origem.
2. Vincular componentes por IFC `GlobalId` e incluir viewpoint/snapshot quando necessário.
3. Definir responsável, prazo, status e regra de escalonamento.
4. Registrar comentários e alterações sem apagar o histórico.
5. Verificar a correção no modelo/IFC atualizado.
6. Encerrar somente com evidência e aprovação previstas no workflow.

## Regras

- Falha IDS pode originar BCF, mas manter referência ao requisito/specification e resultado original.
- Não encerrar issue porque o arquivo foi reenviado; validar a condição de aceite.
- Não alterar issue externa sem autorização.
- Não colocar credenciais, dados sensíveis ou caminhos locais em payloads.
- Separar estado do issue, estado do contêiner no CDE e status/suitability ISO 19650.

## Saída mínima

- ID estável do issue.
- Projeto, modelo, revisão e schema IFC.
- `GlobalId` dos componentes.
- Requisito ou regra violada.
- Responsável, prioridade, prazo e status.
- Evidência de abertura e encerramento.

## Fontes primárias

- BCF-XML: https://github.com/buildingSMART/BCF-XML
- BCF API: https://github.com/buildingSMART/BCF-API
- OpenCDE: https://technical.buildingsmart.org/services/opencde/
