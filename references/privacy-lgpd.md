# Preflight de privacidade e LGPD

Aplicar o ingresso local antes de qualquer inventário, leitura por IA, consulta externa ou delegação IFC. O agente não é a fronteira de segurança: a fronteira é o script local executado antes do LLM.

## Decisões

- `ALLOW`: o scanner determinístico inspecionou um formato suportado e não encontrou indicadores. Prosseguir usando somente o mínimo necessário.
- `LOCAL_ONLY`: o artefato é sensível por definição. Preservar o arquivo byte a byte e permitir leitura pelo coordenador e workers IFC autorizados somente em container isolado, com volume somente leitura; não transferir o arquivo ao Notion, bSDD ou serviços externos não aprovados.
- `REVIEW`: o formato não pôde ser inspecionado integralmente ou houve limitação técnica. Interromper e solicitar revisão humana.
- `BLOCK`: houve indicador de dado pessoal. Não transmitir conteúdo, trecho ou valor a outro agente, modelo, API ou relatório.

Todo IFC/STEP recebe `LOCAL_ONLY`, mesmo sem indicador detectado. Ausência de indicador não prova anonimização nem conformidade legal. O scanner reduz exposição acidental; não substitui base legal, contrato, registro de tratamento, política de retenção ou avaliação jurídica.

## Execução segura

Executar localmente no host, antes de conversar com o OpenClaw:

```powershell
python scripts/privacy_ingest.py "C:\origem\arquivo.ifc" --sensitive-root data/input/sensitive
```

Compartilhar apenas o JSON produzido. Ele fornece `artifact_id` e `agent_path` opacos. Nunca copiar para o prompt o nome/caminho original, conteúdo inspecionado, nomes encontrados ou excertos. A saída contém somente hash, categoria de formato, categorias, contagens e decisão.

## Regras de encaminhamento

1. Receber apenas manifesto seguro, caminho opaco, objetivo e classificação declarada pelo usuário.
2. Para IFC/STEP, rejeitar caminhos fora de `/dados-ifc/sensitive/` ou cujo stem não seja exatamente igual ao `sha256` aprovado.
3. Em `ALLOW`, encaminhar somente o mínimo previsto no manifesto.
4. Em `LOCAL_ONLY`, conferir `integrity_preserved=true`, `local_deterministic_processing_allowed=true`, `llm_content_access_allowed=true`, `authorized_agent_file_access=true`, `external_file_transfer_allowed=false` e hash idêntico antes/depois; permitir leitura apenas aos agentes IFC autorizados no Docker.
5. Em `REVIEW`, interromper e solicitar revisão humana.
6. Em `BLOCK`, pedir uma cópia minimizada quando o formato permitir. Não oferecer o valor detectado como evidência.
7. Não enviar arquivos ao bSDD. Enviar apenas identificadores técnicos previamente liberados.
8. Registrar somente `sha256`, versão da política, decisão, categorias, contagens e aprovação humana aplicável.

## Limites

- PDF, RVT, DWG, NWC e NWD exigem revisão humana por padrão e não são copiados para a área liberada.
- Nomes livres não são detectáveis com segurança sem examinar semanticamente o conteúdo; por isso, declaração do responsável e minimização continuam obrigatórias.
- Em IFC/STEP, `IFCPERSON`, e-mail, telefone, CPF e outros indicadores reforçam a classificação `LOCAL_ONLY`; em outros formatos, continuam causando bloqueio conservador.
- O ingresso cria snapshot byte a byte com nome baseado em SHA-256, eliminando o nome original do fluxo. Não anonimizar, reserializar, normalizar nem regravar o IFC, pois isso romperia a integridade da evidência.
