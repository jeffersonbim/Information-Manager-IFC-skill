# Claude e MCP — execução controlada no Revit

## Papel no fluxo

Usar o MCP como ponte entre Claude e o Revit de produção. Não usar o MCP como fonte normativa do schema nem permitir que subagentes executem mudanças diretamente.

O `revit-mcp-server` permanece em execução e todo o seu catálogo de ferramentas é aprovado para disponibilidade ao Claude executor. Não aplicar denylist permanente por nome de ferramenta. Separar, porém, aprovação da ferramenta e autorização da operação: uma ferramenta disponível só pode produzir escrita quando a chamada concreta estiver coberta por uma SMR aprovada.

```text
Agentes IFC → plano de parâmetros → Sebastian consolida → SMR → aprovação humana
→ Claude executor → MCP Revit → exportação IFC → validação independente
```

## Separação de permissões

### Antes da aprovação

Permitir somente ferramentas MCP de leitura necessárias para confirmar:

- documento, versão e identidade controlada do modelo;
- categorias, famílias, tipos e parâmetros existentes;
- quantidade estimada de elementos afetados;
- conflitos de nome, GUID, tipo de dado e escopo;
- versão e configuração do exportador IFC.

### Depois da aprovação

Executar somente as ferramentas e os argumentos necessários ao `request_id`, revisão, modelo e escopo aprovados. Ferramentas de alcance amplo, como execução de código, comandos genéricos, exclusão, purge, detach, abertura/fechamento, salvamento, sincronização ou exportação externa, permanecem disponíveis, mas exigem menção explícita na SMR quando forem usadas.

## Contrato obrigatório

Antes de cada escrita, conferir:

- `request_id` e revisão da SMR;
- aprovação explícita, responsável e data;
- identificador do modelo de produção;
- ação, categorias, famílias/tipos e parâmetros autorizados;
- estado esperado antes da alteração;
- estratégia de recuperação;
- critério de aceite e exportação IFC requerida.

Interromper se o estado real divergir, se o MCP não identificar inequivocamente o modelo ou se a ferramenta necessária tiver alcance maior que o aprovado.

## Auditoria e retorno

Registrar ferramenta MCP, argumentos minimizados, timestamp, elementos afetados, estado anterior e posterior, itens ignorados, erros e artefato IFC exportado. Não registrar valores pessoais desnecessários.

O retorno do MCP comprova execução no Revit, não conformidade IFC. Sebastian e o validador devem verificar o IFC exportado de forma independente.

## Segurança

- manter o MCP Revit fora do alcance dos workers de análise;
- permitir acesso somente ao Claude executor;
- manter todas as ferramentas do `revit-mcp-server` disponíveis ao Claude executor, sem interpretar disponibilidade como autorização transacional;
- não expor o IFC sensível pelo MCP aos agentes;
- restringir o endpoint MCP entre container e host por allowlist e autenticação;
- não liberar escrita por sessão genérica ou aprovação verbal;
- encerrar a autorização transacional de escrita após concluir ou interromper a SMR; o servidor MCP pode continuar ativo.
