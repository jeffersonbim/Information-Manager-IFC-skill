# Preflight de privacidade e LGPD

Aplicar o ingresso local antes de qualquer inventário, leitura por IA, consulta externa ou delegação IFC. O agente não é a fronteira de segurança: a fronteira é o script local executado antes do LLM.

## Decisões

- `ALLOW`: o scanner determinístico inspecionou um formato suportado e não encontrou indicadores. Prosseguir usando somente o mínimo necessário.
- `REVIEW`: o formato não pôde ser inspecionado integralmente ou houve limitação técnica. Interromper e solicitar revisão humana.
- `BLOCK`: houve indicador de dado pessoal. Não transmitir conteúdo, trecho ou valor a outro agente, modelo, API ou relatório.

Ausência de indicador não prova anonimização nem conformidade legal. O scanner reduz exposição acidental; não substitui base legal, contrato, registro de tratamento, política de retenção ou avaliação jurídica.

## Execução segura

Executar localmente no host, antes de conversar com o OpenClaw:

```powershell
python scripts/privacy_ingest.py "C:\origem\arquivo.ifc" --cleared-root data/input/cleared
```

Compartilhar apenas o JSON produzido. Ele fornece `artifact_id` e `agent_path` opacos. Nunca copiar para o prompt o nome/caminho original, conteúdo inspecionado, nomes encontrados ou excertos. A saída contém somente hash, categoria de formato, categorias, contagens e decisão.

## Regras de encaminhamento

1. Receber apenas manifesto seguro, caminho opaco, objetivo e classificação declarada pelo usuário.
2. Rejeitar caminhos fora de `/dados-ifc/cleared/` ou cujo stem não seja exatamente igual ao `sha256` aprovado.
3. Prosseguir somente se `safe_to_forward` for `true` e `decision` for `ALLOW`.
4. Em `REVIEW`, pedir ao responsável que produza uma cópia minimizada fora do fluxo de IA ou aprove formalmente o risco residual.
5. Em `BLOCK`, pedir uma cópia anonimizada/minimizada. Não oferecer o valor detectado como evidência.
6. Não enviar arquivos ao bSDD. Enviar apenas identificadores técnicos previamente liberados.
7. Registrar somente `sha256`, versão da política, decisão, categorias, contagens e aprovação humana aplicável.

## Limites

- PDF, RVT, DWG, NWC e NWD exigem revisão humana por padrão e não são copiados para a área liberada.
- Nomes livres não são detectáveis com segurança sem examinar semanticamente o conteúdo; por isso, declaração do responsável e minimização continuam obrigatórias.
- `IFCPERSON`, metadados de autoria OOXML, e-mail, telefone formatado, CPF válido e campos de identificadores pessoais causam bloqueio conservador.
- O ingresso cria snapshot com nome baseado em SHA-256, eliminando o nome original do fluxo de IA. O manifesto deve permanecer vinculado a esse hash.
