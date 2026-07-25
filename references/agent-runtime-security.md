# Segurança do runtime de agentes em ambiente corporativo

## Decisão arquitetural

**Status:** aprovado em 2026-07-22.

Em máquina corporativa, não executar agentes IFC diretamente no host. Colocar apenas IfcOpenShell, IfcTester ou scripts dentro do Docker não atende ao requisito: o processo do agente continuaria fora da fronteira de isolamento.

O OpenClaw permanece como runtime autorizado até que o runtime substituto demonstre isolamento equivalente ou superior. A migração para Claude Code somente pode ser aceita quando o processo do coordenador e os processos dos especialistas também forem executados em containers controlados.

## Arquitetura-alvo

Separar dois domínios:

1. **Runtime de agentes:** container com Claude Code e contratos `.claude/agents`, acesso de saída limitado ao serviço de inferência estritamente necessário e sem acesso geral ao host.
2. **Executor determinístico:** container separado, preferencialmente sem rede, com versões fixadas de IfcOpenShell, IfcTester, schemas e scripts aprovados.

O host deve somente iniciar o fluxo, fornecer entradas previamente liberadas e recolher saídas controladas. Nenhum agente recebe acesso direto ao Revit de produção. Alterações no Revit continuam no fluxo Sebastian → SMR → aprovação humana → Claude executor → exportação → validação IFC.

Todo IFC/STEP é classificado como dado sensível e recebe `LOCAL_ONLY`. Preservar o artefato byte a byte sob SHA-256; não anonimizar, reserializar ou regravar. Coordenador e workers IFC autorizados podem abrir o arquivo dentro do Docker em volume somente leitura, mesmo quando houver dados pessoais. Proibir alteração e transferência do arquivo para Notion, bSDD ou destinos externos não aprovados; evitar reproduzir dados pessoais quando não forem necessários ao objetivo técnico.

## Controles obrigatórios

- executar como usuário não root;
- usar filesystem raiz somente leitura;
- remover todas as capabilities Linux e habilitar `no-new-privileges`;
- não montar o socket Docker nem diretórios amplos do host;
- montar originais, schemas e regras aprovadas somente para leitura;
- disponibilizar escrita somente em diretório de saída dedicado e descartável;
- usar `tmpfs` para arquivos temporários e aplicar limites de CPU, memória, processos e tempo;
- manter rede desativada no executor determinístico;
- limitar a saída de rede do runtime de agentes por proxy/allowlist aos endpoints formalmente aprovados;
- isolar o recuperador do Notion em processo/container próprio, com credencial de menor privilégio e sem ferramentas de escrita;
- injetar segredos em tempo de execução; nunca incluí-los na imagem, repositório, prompt ou log;
- bloquear ferramentas de escrita para workers e impedir subdelegação fora do coordenador;
- validar hash e caminho opaco antes de abrir qualquer artefato;
- registrar imagem, digest, versões, manifesto, agente, ferramenta, entrada, saída e aprovação humana;
- destruir o container e os temporários ao final conforme a política corporativa de retenção.

## Critério de aceite da migração

Antes de remover o OpenClaw, executar e registrar testes negativos que comprovem que o agente não consegue:

1. ler arquivos do host fora dos mounts autorizados;
2. modificar IFC, RVT, schemas ou regras montados como somente leitura;
3. gravar fora do diretório de saída;
4. acessar o socket ou a API do Docker;
5. elevar privilégio ou iniciar processo privilegiado;
6. alcançar destinos de rede fora da allowlist;
7. acessar workspace, segredo ou resultado privado de outro agente;
8. contornar o `privacy-gate`, a SMR ou a aprovação humana;
9. declarar conformidade sem evidência determinística e consolidação.

Exigir também testes positivos do parser IFC/IDS, hashes reprodutíveis, versões fixadas e equivalência dos resultados determinísticos entre o runtime atual e o candidato.

## Regra de parada e reversão

Qualquer falha, ausência de evidência ou controle não verificável bloqueia a migração. Manter ou restaurar o OpenClaw como runtime autorizado até a correção e nova aprovação humana. Conveniência, custo ou capacidade do modelo não substituem o critério de isolamento.
