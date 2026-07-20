# Conhecimento 4 — bSDD e Dictionaries API v1

## Objetivo

Consultar dicionários, classes, propriedades, relações e valores permitidos usando a API versionada da buildingSMART.

## API

- Base: `https://api.bsdd.buildingsmart.org/`
- Contrato: https://app.swaggerhub.com/apis/buildingSMART/Dictionaries/v1
- Cliente local: `scripts/bsdd_client.py`

Operações públicas implementadas:

| Operação | Endpoint |
|---|---|
| Listar dicionários | `GET /api/Dictionary/v1` |
| Pesquisar classes | `GET /api/Class/Search/v1` |
| Detalhar classe | `GET /api/Class/v1` |
| Propriedades da classe | `GET /api/Class/Properties/v1` |
| Detalhar propriedade | `GET /api/Property/v5` |
| Pesquisa textual | `GET /api/TextSearch/v2` |

## Processo

1. Selecionar dicionário e versão; não misturar versões silenciosamente.
2. Pesquisar classe e escolher pela URI estável, não apenas pelo nome.
3. Obter detalhes, propriedades, unidades, valores e relações.
4. Registrar Dictionary URI, Class/Property URI, versão, status e data de consulta.
5. Tratar resultado como referência semântica; requisitos contratuais continuam sendo definidos pelo projeto.

## Exemplos

```powershell
python scripts/bsdd_client.py dictionaries --limit 20
python scripts/bsdd_client.py search-classes "wall" --limit 10
python scripts/bsdd_client.py class "https://identifier.buildingsmart.org/uri/buildingsmart/ifc/4.3/class/IfcWall"
```

## Regras

- Enviar `User-Agent` identificável.
- Usar endpoints `/api/.../vX`; não usar `identifier.buildingsmart.org` como API de integração.
- Respeitar paginação, timeout e falhas HTTP.
- Não escrever/uploadar dicionários sem autenticação, autorização e workflow separado.
- Não chamar bSDD de substituto do Classification Manager; ele é serviço governado de conceitos, classes e propriedades.
- Preservar URI, namespace, versão, status e proveniência.

## Fontes primárias

- Documentação da API: https://github.com/buildingSMART/bSDD/blob/master/Documentation/bSDD%20API.md
- Estrutura: https://technical.buildingsmart.org/services/bsdd/data-structure/
- Diretrizes: https://technical.buildingsmart.org/services/bsdd/guidelines/
