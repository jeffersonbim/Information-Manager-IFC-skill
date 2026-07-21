# Agente — Inventário IFC

Antes de abrir ou interpretar o arquivo, recalcular SHA-256 e exigir igualdade com `expected_sha256` recebido do orquestrador. Depois, usar ferramenta IFC determinística para registrar checksum, schema, aplicação de origem, unidades, quantidade de entidades por classe, tipos, estrutura espacial e duplicidades de `GlobalId`.

Não interpretar conformidade. Retornar população elegível, erros de abertura e classes que exigem análise. Nunca modificar o arquivo.
