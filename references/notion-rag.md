# RAG técnico OpenBIM no Notion

Usar o Notion como único catálogo consultivo interno. Tratar fontes oficiais externas como autoridade e arquivos JSON/IDS versionados como regras executáveis.

## Escopo

Consultar apenas:

- `Fontes OpenBIM` para autoridade, versão, URI e escopo;
- `Conceitos OpenBIM` para classes, propriedades, formatos, processos e termos;
- `Regras e Requisitos OpenBIM` para IDS, IDM e critérios genéricos aprovados.
- `Conjuntos de Mapeamentos Revit IFC` para proveniência, escopo, hash e autorização dos snapshots Revit→IFC.

Nunca gravar conversas, prompts, respostas, IFC de projeto, resultados de validação, caminhos locais, dados pessoais ou material confidencial no hub.

## Recuperação obrigatória

1. Ler `references/notion-rag-config.json`.
2. Confirmar o workspace esperado antes de responder.
3. Pesquisar separadamente conceitos, regras e fontes relevantes.
4. Aceitar somente registros com `Status = Aprovado`.
5. Exigir domínio e versão compatíveis com a pergunta.
6. Buscar a página completa de cada resultado selecionado.
7. Retornar identificador, versão, URL oficial, página Notion e trecho técnico resumido.
8. Para Revit→IFC, exigir também `Embeddings autorizados = true` antes de indexar e comparar o SHA-256 do catálogo com o snapshot Git.
9. Se não houver registro aprovado, retornar `KNOWLEDGE_GAP`; não completar por memória.

## Contrato de evidência

```json
{
  "status": "FOUND | KNOWLEDGE_GAP | UNAVAILABLE",
  "query": "pergunta técnica normalizada",
  "schema": "IFC2X3 | IFC4 | IFC4X3 | N/A",
  "records": [
    {
      "code": "identificador do registro",
      "title": "título",
      "version": "versão",
      "domain": "IFC | IDS | IDM | bSDD | ISO 19650 | BCF | Revit-IFC",
      "notion_url": "página consultada",
      "official_url": "fonte primária",
      "status": "Aprovado",
      "summary": "síntese sem extrapolação"
    }
  ],
  "limitations": []
}
```

## Separação de responsabilidades

- Notion: catálogo editorial, aprovação, proveniência e relações.
- Git: versionar skill, schemas, templates e scripts.
- Snapshot Revit→IFC: fornecer linhas normalizadas ao parser determinístico; nunca substituir o catálogo Notion.
- JSON/IDS: representar regra executável com versão e hash.
- Ferramenta determinística: produzir conformidade.
- IA: rotear, explicar e citar sem alterar o resultado do validador.

O RAG reduz respostas sem fonte; não transforma texto consultivo em regra determinística.
