# Revit→IFC, RAG e OpenClaw em VPS

## Papel do mapeamento

Usar o mapeamento para gerar candidatos rastreáveis, nunca para declarar classe IFC apenas por semelhança textual. Encadear categoria Revit, configuração de exportação, classe e `PredefinedType`, Pset/propriedade, schema aplicável, requisito IDS/IDM e objeto exportado.

## Camadas

1. Notion: catálogo editorial, aprovação, versão, hash e relações.
2. Git: snapshots e regras executáveis versionados.
3. Parser: consulta exata por GUID, nome, Pset, propriedade, tipo de dado e escopo.
4. Índice vetorial: recuperação semântica somente de conjuntos aprovados e autorizados.
5. Validador IFC/IDS: resultado determinístico.
6. Agente: roteamento, explicação, citações e lacunas.

## VPS

Executar OpenClaw, banco vetorial e sincronizador em serviços separados. Instalar no processo do recuperador apenas o MCP Notion oficial com `notion-search`, `notion-fetch` e `notion-get-self`. Usar um usuário OAuth dedicado, com MFA e acesso exclusivo ao hub OpenBIM. O OAuth hospedado herda permissões do usuário e não fornece credencial read-only; a vedação de escrita depende do filtro de ferramentas, do isolamento do Gateway e da auditoria.

Minimizar consultas antes do MCP. Não gravar perguntas ou respostas no Notion, mas assumir que tool calls podem permanecer em transcritos OpenClaw. Configurar redação, retenção curta e limpeza periódica de sessões e logs.

Não permitir que agentes criem relações aprovadas autonomamente. Eles podem propor uma relação como `Rascunho`, com evidência e hash. A promoção para `Aprovado` e a autorização de embeddings exigem revisão humana. Reindexar apenas conteúdo aprovado cujo hash mudou.

## Precisão

A precisão tende a melhorar porque o universo de candidatos fica menor e rastreável. Não há garantia automática: mapeamentos sem versão, categoria ambígua, configurações específicas do exportador e ausência de teste pós-exportação continuam gerando `KNOWLEDGE_GAP` ou revisão humana.
