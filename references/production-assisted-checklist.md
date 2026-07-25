# Checklist de produção assistida

## Critério de entrada

A skill pode iniciar um ciclo de produção assistida quando:

- a versão Git e os hashes dos artefatos estiverem registrados;
- o questionário canônico tiver exatamente seis gates e passar nos testes;
- o template de entrada/saída estiver validado;
- o runtime fixado estiver disponível ou a limitação estiver explicitamente
  aceita para um ensaio que não dependa de IFC/IDS;
- houver ao menos uma amostra representativa exportada do Revit;
- existir responsável humano pela decisão de cada gate;
- houver cópia recuperável dos artefatos e procedimento de rollback.

## Critério de homologação

Não declarar homologação plena antes de:

- `IfcOpenShell` e `IfcTester` passarem na verificação da versão fixada;
- executar os seis gates em caso positivo, negativo e não aplicável;
- comprovar no IFC os destinos `ATTRIBUTE`, `Qto`, `Pset` e associação usados;
- validar o IDS no XSD e confirmar cobertura diferente de `0/0`;
- reconciliar o consolidado com o último modelo analisado;
- registrar aprovação humana final.

## Política de correções

Podem entrar como versão `PATCH`, sem reabrir todo o ciclo:

- ortografia, formatação e links;
- esclarecimento que não altera decisão;
- exemplos adicionais que não alteram regras;
- correções visuais do dashboard ou planilha.

Exigem versão `MINOR` e revalidação dos gates afetados:

- nova pergunta orientadora sem mudar o número de gates;
- nova categoria, disciplina ou exemplo;
- campo adicional de evidência;
- melhoria compatível no relatório.

Exigem versão `MAJOR` e novo ciclo completo:

- mudança de schema IFC ou versão IDS;
- alteração de regra de aprovação ou cardinalidade;
- mudança entre atributo, Qto, Pset ou associação;
- alteração de datatype, unidade, fórmula ou método de medição;
- mudança na applicability do IDS;
- alteração de runtime ou ferramenta determinística.
