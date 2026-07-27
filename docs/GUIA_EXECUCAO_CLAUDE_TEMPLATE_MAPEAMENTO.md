# Execução em outra máquina — template, Notion e agentes Claude Code

Este roteiro permite que a skill seja instalada em outra máquina e utilizada por
agentes Claude Code para analisar a matriz de requisitos e preparar os
artefatos técnicos dos seis gates.

## Princípio operacional

O Notion é o catálogo consultivo que controla quais conjuntos Revit–IFC estão
aprovados. Os snapshots Git e o parser local produzem a consulta determinística.
O agente não deve substituir essa sequência por memória ou por simples
coincidência de nomes.

`Template Excel → requisito normalizado → recuperador Notion → parser determinístico → planejador de parâmetros → Saida_Mapeamento → prova IFC → IDS`

## Instalação

1. Clone este repositório inteiro. Não copie somente um `SKILL.md` isolado,
   pois os agentes dependem de `references/`, `scripts/`, `templates/`,
   `.claude/` e `openclaw/`.
2. Abra o Claude Code na raiz do repositório.
3. Configure o MCP oficial do Notion e conclua o OAuth com uma conta que tenha
   acesso ao hub **OpenBIM Knowledge RAG**.
4. Mantenha o Notion em leitura: agentes não criam, aprovam ou alteram registros
   no hub.
5. Execute os agentes de análise em ambiente isolado conforme
   `references/agent-runtime-security.md`. O executor Claude/Revit MCP é
   separado e só atua após aprovação humana de uma SMR.

## Consulta de mapeamento para uma matriz Excel

1. Anexe `templates/Template_Consulta_Parametros_Revit_IFC.xlsx` preenchido na
   conversa. O anexo é o gatilho: o coordenador inicia a ingestão sem exigir um
   comando adicional.
2. O coordenador executa `scripts/template_intake.py`, lê cada linha da aba
   `Entrada_Requisitos` e separa a entrada em `ready` e `blocked`.
3. Somente linhas `ready` — com código, descrição,
   disciplina, categoria Revit e schema IFC.
   — acionam o `openbim-knowledge-retriever` e o
   `ifc-parameter-planner`. Linhas `blocked` retornam com os campos ausentes e
   não são enviadas aos agentes técnicos.
4. O `openbim-knowledge-retriever` consulta no Notion somente conjuntos
   `Aprovado`, confere o SHA-256 e retorna a fonte aplicável.
5. O `ifc-parameter-planner` consulta a base local com, por exemplo:

   ```powershell
   python scripts/parameter_mappings.py query <nome-do-parametro> --scope instance
   python scripts/parameter_mappings.py query <nome-do-parametro> --scope type
   ```

6. O planejador separa origem Revit e destino IFC. Ele registra candidato,
   escopo, tipo de dado, fonte, arquivo e linha da evidência.
7. O agente não chama uma relação de “aprovada” somente porque ela existe no
   catálogo. A saída deve ser `MAPEADO_PENDENTE_PROVA_IFC`,
   `CANDIDATO_A_REVISAR` ou `REVISAO_HUMANA`, conforme a evidência disponível.
8. Preencha a aba `Saida_Mapeamento`; não sobrescreva os requisitos originais
   na aba de entrada.

## Artefatos esperados por gate

| Gate | Artefato que o agente prepara ou atualiza |
|---|---|
| 1 — Requisitos | `Entrada_Requisitos` preenchida e requisitos bloqueados identificados |
| 2 — Origem | inventário de parâmetros nativos/compartilhados e candidatos por escopo |
| 3 — Arquitetura | `Saida_Mapeamento`, SMR e, após aprovação explícita da linha, TXT de parâmetros compartilhados, manifesto XML do Shared Parameters Tool, TXT de Psets, XML do Model Checker e plano JSON para Bonsai |
| 4 — Exportação | configuração de exportação, IFC de prova e evidência por `GlobalId` |
| 5 — IDS | IDS por disciplina, somente para destinos comprovados no IFC |
| 6 — Validação | relatório IDS, falhas por requisito/`GlobalId` e consolidado do último modelo |

## Limites obrigatórios

- O Notion não recebe IFC, planilhas de projeto, conversas ou resultados de
  validação.
- O parser retorna candidatos; schema e IFC exportado são a prova final.
- Sem correspondência confiável, usar `REVISAO_HUMANA` ou `KNOWLEDGE_GAP`.
- Não criar Pset ou Qto customizado automaticamente.
- Não editar Revit sem SMR aprovada e autorização humana explícita.

## Geração física no Gate 3

Depois que o responsável aprovar uma linha com
`Aprovacao_Gate_3=APROVADO`, o coordenador prepara um JSON com as linhas
aprovadas e executa:

```powershell
python scripts/gate3_artifacts.py matriz_aprovada.json --output output/gate3
```

O gerador recusa parâmetro compartilhado sem GUID válido e não inclui linhas
pendentes. O XML do Shared Parameters Tool é um manifesto de configuração
auditável: a compatibilidade de importação deve ser confirmada na versão do add-in
instalada. O XML do Model Checker segue o checkset da Autodesk. Nenhum desses
artefatos é evidência de IFC; a prova permanece no Gate 4.

## Referências

- `SKILL.md`
- `CLAUDE.md`
- `references/parameter-mappings.md`
- `references/agent-parameter-planner.md`
- `references/agent-openbim-knowledge-retriever.md`
- `docs/GUIA_OPERACIONAL_SEIS_GATES_IFC.md`
