# Entrada de documentos IFC

Não coloque IFC diretamente nesta raiz. Execute `scripts/privacy_ingest.py` e armazene o snapshot íntegro na subpasta `sensitive`, com nome baseado no SHA-256.

No runtime isolado, a pasta aparece como `/dados-ifc` em modo somente leitura. Todo IFC é `LOCAL_ONLY`: coordenador e workers IFC autorizados podem abrir `/dados-ifc/sensitive/<sha256>.ifc`, inclusive quando houver dados pessoais. É proibido modificar ou transferir o arquivo para destinos externos não aprovados.

Exemplo de referência em uma solicitação:

`Analise deterministicamente /dados-ifc/sensitive/<sha256>.ifc, confirme o hash e forneça aos agentes somente a saída minimizada.`
