# Handoff para Claude — validação e liberação para produção

**Projeto:** Information Manager IFC
**Data:** 2026-07-22
**Responsável conceitual:** Sebastian
**Executor Revit:** Claude via `revit-mcp-server`
**Status:** release candidate local; não liberada para produção

## Objetivo

Continuar a integração e validação da equipe de agentes que recebe IFC, inventaria o modelo, relaciona classes e parâmetros, classifica ações autorais e prepara alterações controladas no Revit. Concluir somente com evidências de isolamento, integridade, funcionamento dos agentes, execução MCP controlada, rollback, exportação e validação independente.

## Leitura obrigatória

Antes de agir, ler integralmente:

1. `CLAUDE.md`;
2. `.claude/skills/information-manager-ifc/SKILL.md`;
3. `SKILL.md`;
4. `references/agent-runtime-security.md`;
5. `references/privacy-lgpd.md`;
6. `references/agent-orchestrator.md`;
7. `references/agent-parameter-planner.md`;
8. `references/revit-mcp-execution.md`;
9. `references/parameter-mappings.md`;
10. `docs/MANUAL-RAG-REVIT-IFC-OPENCLAW-VPS.md`.

Há alterações locais do usuário. Não descartar, restaurar ou reformatar mudanças existentes. Não usar `git reset --hard` ou equivalente.

## Decisões aprovadas

### Equipe principal

- `ifc-coordinator`: Sebastian, coordenador conceitual;
- `ifc-inventory`: inventário determinístico;
- `ifc-mapping-validator`: categoria Revit, classe IFC, `PredefinedType` e resultado;
- `ifc-parameter-planner`: relação e classificação de parâmetros;
- `ifc-consolidator`: reconciliação, cobertura e relatório.

Relações complexas, IDS, bSDD, BCF e Notion são opcionais.

### Classificações permitidas

- `NATIVO_REVIT`;
- `NATIVO_IFC`;
- `CONFIGURACAO_EXPORTACAO`;
- `PARAMETRO_COMPARTILHADO`;
- `PARAMETRO_PROJETO`;
- `CALCULADO`;
- `NAO_APLICAVEL`;
- `NAO_VERIFICAVEL`;
- `CONFLITO`;
- `REVISAO_HUMANA`.

Cada classificação exige evidência do schema, Pset, mapeamento aprovado, arquivo/linha da fonte e contexto Revit quando aplicável.

### IFC e dados pessoais

- Tratar todo IFC/STEP como `sensitive_personal_data` e `LOCAL_ONLY`.
- Não anonimizar, normalizar, reserializar nem regravar.
- Criar snapshot byte a byte nomeado pelo SHA-256.
- Coordenador e workers IFC autorizados podem ler o IFC dentro do Docker, inclusive com dados pessoais.
- Montar o arquivo somente para leitura e verificar SHA-256 antes/depois.
- Não modificar nem transferir o IFC ao Notion, bSDD ou serviços externos não aprovados.
- Evitar reproduzir dados pessoais sem necessidade técnica.

Manifesto esperado:

```json
{
  "decision": "LOCAL_ONLY",
  "safe_to_forward": false,
  "local_deterministic_processing_allowed": true,
  "llm_content_access_allowed": true,
  "authorized_agent_file_access": true,
  "external_file_transfer_allowed": false,
  "integrity_preserved": true,
  "data_classification": "sensitive_personal_data"
}
```

### Docker

- OpenClaw permanece autorizado até o runtime Claude containerizado demonstrar isolamento equivalente.
- Não executar agentes IFC no host corporativo.
- Fixar `ifcopenshell==0.8.5` e `ifctester==0.8.5`.
- Usar usuário não root, rootfs somente leitura, `capDrop: ALL`, sem Docker socket e rede desativada por padrão.
- Montar IFC, schemas e regras como somente leitura; saída em diretório separado.

### Claude e MCP Revit

- Servidor: `revit-mcp-server`, iniciado por `npx revit-mcp-server`.
- Pacote local identificado: versão `2.0.1`.
- Último diagnóstico: `Failed to connect`.
- O MCP continuará ativo e todo o catálogo é aprovado para disponibilidade ao Claude executor.
- Ferramenta disponível não significa operação automaticamente autorizada.
- Subagentes não recebem MCP Revit.
- Antes da SMR: leitura para estimar impacto.
- Escritas exigem `request_id`, revisão, modelo, alvo e argumentos aprovados.
- Ao concluir a SMR, encerra-se a autorização transacional; o servidor permanece ativo.

## Fluxo aprovado

```text
IFC íntegro → privacy_ingest/SHA-256 → LOCAL_ONLY → Docker somente leitura
→ inventário → mapeamento → planejamento de parâmetros → consolidação Sebastian
→ SMR → aprovação humana → Claude/MCP/Revit → exportação IFC
→ validação independente → aceite humano
```

## Ingresso IFC

```powershell
python scripts/privacy_ingest.py "C:\origem\modelo.ifc" `
  --sensitive-root data/input/sensitive
```

Delegar apenas `/dados-ifc/sensitive/<sha256>.ifc`. Nunca usar nome/caminho original.

## Estado local conhecido

Já foram implementados:

- política `LOCAL_ONLY` com leitura por agentes autorizados;
- snapshot íntegro e verificação SHA-256;
- proibição de transferência externa;
- agentes Claude e OpenClaw;
- `ifc-parameter-planner`;
- contrato de planejamento de parâmetros;
- contrato Claude–MCP–Revit;
- segurança do runtime corporativo;
- documentação e testes.

Verificar antes de mudar:

```powershell
git status -sb
git diff --check
git diff --stat
```

Última validação: 37 testes aprovados, `py_compile` aprovado e `git diff --check` sem erros. Reexecutar:

```powershell
python -m unittest discover -s tests -v
python -m py_compile scripts/privacy_gate.py scripts/privacy_ingest.py
git diff --check
```

Fallback Python no Windows:

```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe" `
  -m unittest discover -s tests -v
```

## Ferramentas MCP relevantes

Leitura: `get_project_info`, `get_model_statistics`, `get_elements`, `get_parameters`, `get_families`, `get_selected_elements`, `get_current_view_elements`, `get_materials`, `get_phases`, `get_worksharing_info`, `validate_parameters`, `get_warnings`.

Parâmetros: `add_shared_parameter`, `modify_parameter`, `batch_modify_parameters`, `bulk_parameter_transfer`, `import_data_from_csv`, `change_type`.

Recuperação: `create_checkpoint`, `rollback_to_checkpoint`, `undo_last_operation`, `save_document`, `sync_to_central`.

Alto impacto: `send_code_to_revit`, `post_command`, `delete_elements`, `purge_unused`, `deep_purge`, `convert_category`, `detach_from_central`, `save_as_document` e integrações externas. Permanecem disponíveis, mas a chamada concreta precisa estar coberta pela SMR.

## Plano de execução restante

### 1. Estabilizar o checkout

1. Ler os arquivos obrigatórios.
2. Inspecionar o diff completo.
3. Remover contradições entre leitura IFC autorizada e transferência externa proibida.
4. Confirmar equipe mínima nos dois runtimes.
5. Reexecutar testes.

### 2. Validar Docker

1. Confirmar Docker CLI/Desktop.
2. Construir a imagem fixada.
3. Confirmar versões do IfcOpenShell/IfcTester.
4. Confirmar usuário não root, rootfs `ro`, capabilities removidas e ausência do Docker socket.
5. Montar `data/input/sensitive:/dados-ifc/sensitive:ro`.
6. Usar mount de saída separado.
7. Registrar imagem e digest.

### 3. Testar IFC controlado

Solicitar um IFC de teste autorizado; não escolher arquivo corporativo arbitrariamente.

1. Executar `privacy_ingest.py`.
2. Validar manifesto `LOCAL_ONLY`.
3. Registrar SHA-256 inicial.
4. Abrir no Docker/IfcOpenShell.
5. Inventariar schema, classes, Psets, propriedades, tipos e ocorrências.
6. Confirmar SHA-256 final idêntico.
7. Comprovar ausência de escrita e transferência externa.

### 4. Testar agentes

Usar caso pequeno com `IfcDoor` e `IfcWindow`: Altura, Largura, Material, Área, Código PP, `Export to IFC As`/`IfcExportAs` e `IFC Predefined Type`/`IfcExportType`.

Exigir do Planejador: classificação, ação (`CREATE`, `REUSE`, `MAP`, `CALCULATE`, `REMOVE_DUPLICATE`, `NO_ACTION`, `REVIEW`), schema, classe, aplicabilidade do `PredefinedType`, instância/tipo, Pset/propriedade, tipo de dado, categoria Revit, GUID conhecido/pendente, evidência, limitações e aprovação humana.

### 5. Conectar MCP Revit

1. Abrir Revit com add-in correspondente.
2. Executar `claude mcp list` e confirmar conexão.
3. Consultar `tools/list` ao vivo e comparar com a versão `2.0.1`.
4. Não executar escrita durante descoberta.
5. Testar leitura em modelo controlado.
6. Registrar versões do Revit, add-in, MCP e exportador IFC.

### 6. SMR e rollback

1. Sebastian produz SMR de teste.
2. Claude estima impacto.
3. Aguardar aprovação explícita.
4. Criar checkpoint.
5. Executar alteração pequena e reversível.
6. Testar `undo_last_operation`/`rollback_to_checkpoint`.
7. Confirmar retorno ao estado anterior.

### 7. Exportar e validar

1. Exportar inicialmente IFC2X3.
2. Registrar hash.
3. Validar classe, `PredefinedType` aplicável, Psets, propriedades, valores e `GlobalId`.
4. Informar cobertura, falhas e itens não verificáveis.
5. Não declarar conformidade apenas porque o MCP não retornou erro.

### 8. Testes negativos

Em ambiente de teste e sem ações destrutivas na produção, verificar tentativa de: alterar IFC `ro`; acessar host fora dos mounts; acessar Docker socket; transferir IFC externamente; escrever no Revit sem SMR; chamar MCP com alvo divergente; declarar conformidade sem evidência; usar mapeamento não aprovado.

## Critérios de produção

Declarar `PRODUCTION_READY` somente quando:

- alterações revisadas e testes aprovados;
- Docker reproduzível e isolado;
- IFC íntegro antes/depois;
- agentes inventariam, mapeiam e planejam parâmetros;
- nenhum worker modifica IFC ou Revit;
- MCP conectado e catálogo confirmado ao vivo;
- checkpoint e rollback testados;
- alteração pequena executada por SMR aprovada;
- IFC exportado e validado independentemente;
- testes negativos registrados;
- riscos aceitos e aprovação humana final;
- alterações publicadas no GitHub.

Caso contrário, retornar `RELEASE_CANDIDATE` ou `BLOCKED`.

## Git

Não publicar antes das verificações e autorização. Depois:

1. criar branch `agent/validacao-producao-ifc`;
2. adicionar somente arquivos deste trabalho;
3. commit objetivo;
4. push;
5. PR em rascunho com testes e limitações;
6. aguardar revisão e autorização para merge.

Não criar tag `v1.0.0-production` antes de atender todos os critérios.

## Regras de parada

Interromper e pedir decisão humana se faltar IFC autorizado, Docker/MCP estiver indisponível, o hash mudar, houver escrita sem SMR, o modelo ativo for ambíguo, a chamada MCP exceder o escopo, houver risco de perda/sync não previsto, o teste exigir transferência externa ou faltar evidência determinística.

## Atualização ao responsável

```text
Status: READY | WARNING | BLOCKED
Fase:
Concluído:
Evidência:
Pendência:
Próxima ação:
Requer aprovação humana: sim | não
```

Não repetir todo este documento em cada resposta. Continuar da última evidência válida.

## Status ao encerrar sessão (2026-07-22, máquina corporativa)

Sessão interrompida para continuar em máquina pessoal. Estado abaixo é a última evidência válida — ler antes de qualquer nova ação.

**Status:** BLOCKED (produção). RELEASE_CANDIDATE local mantido.

### Concluído nesta sessão

1. Checkout estabilizado: `git status -sb`, `git diff --check` (sem erro, só avisos CRLF) e `git diff --stat` revisados. Nada descartado, nenhum `git reset` usado.
2. `python -m unittest discover -s tests -v` → 37/37 OK.
3. `python -m py_compile scripts/privacy_gate.py scripts/privacy_ingest.py` → OK.
4. `python scripts/verify_ifc_runtime.py` → `ifcopenshell 0.8.5` + `ifctester 0.8.5`, `safe_to_execute: true`.
5. Ingresso de privacidade rodado nos 6 IFC reais em `../IFC/` (pasta irmã da skill, fora dela — repo raiz é `0000_pset_compo`, skill fica em `Information-Manager-IFC-skill/`):
   - `20260001-0000-3D-PB-3D-0001.ifc`, `20260002-0000-3D-PC-3D-0001_.ifc`, `-0003.ifc`, `-0004.ifc`, `-0007.ifc`, `-0009.ifc`.
   - Todos `LOCAL_ONLY`, `safe_to_forward: false`, hash íntegro (nome do arquivo em `data/input/sensitive/` = SHA-256 recalculado, conferido com `sha256sum`).
   - Achados PII (só contagem, sem valor exposto): CPF, email, telefone BR, `IfcPerson`/`IfcOrganization` em todos os 6. Maior concentração no arquivo `-0003.ifc` (18 CPF, 245 email, 1053 telefone).
   - Autorização de escolha do arquivo: usuário indicou explicitamente "use os ifc que estão na pasta IFC" — não foi escolha unilateral do agente.
6. MCP `revit-mcp-server@2.0.1` conectado e catálogo completo carregado (bate com handoff + tools extras não documentadas: `ai_*`, `export_to_notion`, `export_to_powerbi`, `google_sign_in`, etc. — vale atualizar a lista "Ferramentas MCP relevantes" numa próxima revisão).
7. **Achado importante:** o add-in Revit ("Revit MCP Plugin") tem um `CommandSet` próprio com apenas **23 comandos habilitados** nas Settings do plugin — não é 1:1 com o catálogo de tools do pacote npm. Mapeamento confirmado lendo o código-fonte (`build/tools/*.js`, `sendCommand("...")`):
   - Funcionam (comando habilitado bate com o que a tool envia): `get_current_view_info`, `get_current_view_elements`, `get_selected_elements`, `get_families` (envia `get_available_family_types`, que está habilitado).
   - **Não funcionam agora** (comando enviado não está no CommandSet habilitado; qualquer chamada trava ~300s sem erro): `get_project_info`, `get_model_statistics` (add-in só tem `analyze_model_statistics`, nome diferente), `get_worksharing_info`, `validate_parameters`, `get_phases`, `get_materials` (add-in só tem `get_material_quantities`, nome diferente).
   - Usuário decidiu **adiar a correção desse gap para atualização futura** — não é bloqueio ativo, é pendência conhecida.
8. Testes de leitura reais confirmados: `get_current_view_info` (view `{3D}`, 1451 elementos), `get_current_view_elements` (dado real, paredes ".SUP-ALVENARIA..." — confirma modelo de produção real aberto), `get_families` (3810 linhas de tipos), `get_selected_elements` (`[]`, nada selecionado).
9. Nenhuma escrita, nenhuma SMR, nenhum checkpoint. Nada publicado no GitHub.

### Pendências (nesta ordem de bloqueio)

1. **Docker**: nesta máquina corporativa, `docker info` retornava erro 500 (`dockerDesktopLinuxEngine`) e o WSL `docker-desktop` ficava preso em `Stopped` mesmo após `Stop-Process -Force` + `wsl --shutdown` + relançar `Docker Desktop.exe` (2 tentativas, incluindo um popup "Lingering processes detected" que precisou intervenção manual do usuário). Não resolvido ao encerrar sessão. **Pode não se aplicar na máquina pessoal** — testar do zero lá.
2. Sem Docker: inventário determinístico (IfcOpenShell) dos 6 IFC ainda não rodou. Isso bloqueia mapeamento e planejamento de parâmetros reais (Etapas 3-4 do plano).
3. Identidade formal do projeto Revit (nome/número) e versões (Revit, add-in, exportador IFC) não confirmadas — depende de habilitar mais comandos no CommandSet do add-in ou achar equivalente.
4. Nenhuma SMR existe. Antes de qualquer escrita/checkpoint: Sebastian formula a SMR, usuário aprova explicitamente.
5. Exportação IFC + validação independente, testes negativos, aceite humano final e publicação no GitHub — nenhum feito ainda.

### Próxima ação recomendada na máquina pessoal

1. Repetir verificação de estado (`git status -sb`, testes, `verify_ifc_runtime.py`) — não presumir que nada mudou só porque foi copiado.
2. Testar Docker do zero (`docker info`, `docker images`); se funcionar, seguir plano a partir da Etapa 2 (construir imagem fixada).
3. Reconectar `revit-mcp-server` se for continuar com Revit na máquina pessoal (senão essa parte fica pausada).
4. Não repetir ingresso dos 6 IFC se a pasta `data/input/sensitive/` viajar junto (snapshots + manifests já existem e são válidos, hash não muda).
