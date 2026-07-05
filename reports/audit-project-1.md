================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~785 lines of code
Date:    2026-07-05

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 4 | LOW: 3
Total: 17 findings

## Findings

### [CRITICAL] SQL Injection por concatenação de string (C2)
- **File:** `models.py:28,48-49,58-60,68,92,110-111,127-129,140,148-166,174,280,289-297`
- **Description:** Praticamente todas as queries montam SQL concatenando entrada do usuário (`"... WHERE id = " + str(id)`, `LIKE '%" + termo + "%'`, login com email/senha concatenados).
- **Impact:** Um atacante lê/altera/apaga o banco inteiro; o login é bypassável com `' OR '1'='1`.
- **Recommendation:** Queries parametrizadas com placeholders `?` (playbook P2).

### [CRITICAL] God File / God Class multi-domínio (C3)
- **File:** `models.py:1-315` e `controllers.py:1-293`
- **Description:** Um único `models.py` concentra acesso a dados, regra de negócio, cálculo e validação para 4 domínios (produtos, usuários, pedidos, relatórios); `controllers.py` repete o padrão.
- **Impact:** Impossível testar em isolamento; qualquer mudança arrisca quebrar tudo; viola totalmente o SRP.
- **Recommendation:** Separar em models e controllers por domínio + camada de services (P3).

### [CRITICAL] Credenciais hardcoded e vazamento de segredo (C1)
- **File:** `app.py:7` (SECRET_KEY), `controllers.py:289` (`secret_key` exposta no `/health`)
- **Description:** `SECRET_KEY = "minha-chave-super-secreta-123"` no código e ainda devolvida no corpo do endpoint `/health`.
- **Impact:** Segredo versionado no Git e exposto publicamente por HTTP → sessões forjáveis.
- **Recommendation:** Ler de variável de ambiente via módulo de config; nunca serializar segredo (P1).

### [CRITICAL] Endpoints administrativos perigosos (C4)
- **File:** `app.py:59-78` (`/admin/query`), `app.py:47-57` (`/admin/reset-db`)
- **Description:** `/admin/query` executa SQL arbitrário vindo do body; `/admin/reset-db` apaga todas as tabelas — ambos sem autenticação.
- **Impact:** SQL arbitrário (equivalente a RCE no banco) e destruição total de dados por qualquer um.
- **Recommendation:** Remover `/admin/query` (não há como torná-lo seguro) e proteger/remover `/admin/reset-db`.

### [CRITICAL] Senhas em texto puro (C5)
- **File:** `database.py:76-78` (seed), `models.py:122-131` (create), `models.py:105-120` (login)
- **Description:** Senhas são gravadas e comparadas em texto puro no banco.
- **Impact:** Vazamento do banco expõe todas as senhas reais dos usuários.
- **Recommendation:** Hash com salt (bcrypt/argon2; PBKDF2 da stdlib como mínimo) — playbook P9.

### [HIGH] Regra de negócio na camada errada (H1)
- **File:** `models.py:133-169` (criar_pedido: estoque/total), `models.py:235-273` (relatório: desconto)
- **Description:** Cálculo de total, checagem de estoque e faixas de desconto vivem misturados ao acesso a dados.
- **Impact:** Regra não reutilizável nem testável isoladamente; acoplada ao SQL.
- **Recommendation:** Mover para `services/pedido_service` e `services/relatorio_service` (P4).

### [HIGH] Estado global mutável (H2)
- **File:** `database.py:4-5` (`db_connection = None`, `db_path` globais)
- **Description:** Conexão de banco mantida em variável global de módulo.
- **Impact:** Acoplamento forte, difícil de testar/paralelizar, sem controle de ciclo de vida.
- **Recommendation:** Factory de conexão injetada nos models (P6).

### [HIGH] Ausência de injeção de dependência (H3)
- **File:** `controllers.py:2-3`, `models.py:1`
- **Description:** Controllers importam `models` concretamente e models importam `get_db` diretamente; nada é injetável.
- **Impact:** Impossível trocar o DB por um mock; camadas soldadas umas às outras (viola DIP).
- **Recommendation:** Injetar models/services via construtor no composition root (P6).

### [HIGH] Vazamento de dado sensível na serialização (H5)
- **File:** `models.py:79-87` (get_todos_usuarios), `models.py:94-102` (get_usuario_por_id)
- **Description:** A serialização de usuário inclui o campo `senha`.
- **Impact:** `GET /usuarios` expõe as senhas de todos os usuários.
- **Recommendation:** Serializador público que omite `senha` (P9/guidelines Model).

### [HIGH] Efeitos colaterais simulados dentro do controller (H1)
- **File:** `controllers.py:208-210,247-250`
- **Description:** "Envio" de email/SMS/push via `print` embutido no fluxo do controller.
- **Impact:** Controller acumula responsabilidade de notificação; não testável, não desacoplado.
- **Recommendation:** Extrair para um `notification_service` injetado (P12).

### [MEDIUM] Query N+1 na listagem de pedidos (M1)
- **File:** `models.py:187-199` e `models.py:219-231`
- **Description:** Para cada pedido busca os itens em query separada e, dentro, uma query por item para o nome do produto.
- **Impact:** Número de queries cresce linearmente com pedidos×itens → latência.
- **Recommendation:** Carregar itens com um único JOIN por lote de pedidos (P7).

### [MEDIUM] Validação duplicada e divergente (M2/M3)
- **File:** `controllers.py:28-54` vs `controllers.py:72-90`
- **Description:** As validações de criar e atualizar produto são copiadas com pequenas diferenças.
- **Impact:** Regras divergem silenciosamente; manutenção multiplicada.
- **Recommendation:** Função de validação única reutilizada por ambos (P11).

### [MEDIUM] Tratamento de erro genérico e vazando detalhes (M4)
- **File:** `controllers.py:10-12,21-22,60-62,95-96` (padrão repetido em todos os handlers)
- **Description:** Cada handler tem `except Exception` devolvendo `str(e)` ao cliente.
- **Impact:** Vaza detalhes internos, código repetido, sem log estruturado.
- **Recommendation:** Error handler centralizado (P5).

### [MEDIUM] Operações relacionadas sem transação explícita (M5)
- **File:** `models.py:148-168`
- **Description:** Inserção de pedido, itens e baixa de estoque em commits soltos, sem rollback coeso.
- **Impact:** Falha no meio deixa pedido/itens/estoque inconsistentes.
- **Recommendation:** Agrupar em uma única transação (P5/model).

### [LOW] Magic numbers nas faixas de desconto (L1)
- **File:** `models.py:257-262`
- **Description:** `10000`, `5000`, `1000`, `0.1`, `0.05`, `0.02` soltos no cálculo.
- **Impact:** Intenção obscura, mudança arriscada.
- **Recommendation:** Constante nomeada `DESCONTO_FAIXAS` (P4).

### [LOW] Logging via print (L2)
- **File:** `app.py:56,83-86`, `controllers.py:8,11,57,61,179,182,208-210`
- **Description:** Uso de `print` para logs de aplicação.
- **Impact:** Sem níveis nem estrutura; polui stdout.
- **Recommendation:** Módulo `logging` (P12).

### [LOW] Flags inseguras por padrão (L5)
- **File:** `app.py:8` (`DEBUG = True`), `app.py:88` (`debug=True`)
- **Description:** Debug ligado fixamente, inclusive no `app.run`.
- **Impact:** Stack traces e console interativo expostos em produção.
- **Recommendation:** Flag por variável de ambiente (P1).

## Deprecated APIs
| API | File:Line | Replace with |
|---|---|---|
| — | — | Nenhuma API deprecated detectada (SQLite via `sqlite3` parametrizado é o alvo recomendado) |

## Refactoring plan (preview da Fase 3)
- P1 → `src/config/settings.py` lê segredos/flags de env; `/health` deixa de expor segredo.
- P2 → todas as queries parametrizadas nos models.
- P3 → God File quebrado em `models/{produto,usuario,pedido}_model.py` + controllers por domínio.
- P4 → regra de estoque/total/desconto movida para `services/{pedido,relatorio}_service.py`.
- P5 → `middlewares/error_handler.py` centraliza erros; controllers levantam `DomainError`.
- P6 → conexão via factory injetada; fim do estado global.
- P7 → N+1 resolvido com JOIN por lote.
- P9 → senhas com PBKDF2+salt; serialização omite `senha`.
- P12 → notificações via `notification_service`; `print` → `logging`.
- C4 → `/admin/query` e `/admin/reset-db` removidos.

================================
Total: 17 findings
================================
