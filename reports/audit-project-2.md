================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   Node.js + Express 4.18 (SQLite via sqlite3 5.1)
Files:   3 analyzed | ~180 lines of code
Date:    2026-07-05

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 3 | LOW: 2
Total: 11 findings

## Findings

### [CRITICAL] Credenciais hardcoded e dado sensível em log (C1)
- **File:** `src/utils.js:1-7`, `src/AppManager.js:45`
- **Description:** `dbPass`, `paymentGatewayKey` (`pk_live_...`) e `smtpUser` fixos no código; o handler de checkout ainda faz `console.log` do **número do cartão** e da chave do gateway.
- **Impact:** Chave de produção de pagamento versionada no Git e dados de cartão em log → violação grave de segurança/PCI.
- **Recommendation:** Config via variáveis de ambiente; nunca logar cartão/segredo (playbook P1).

### [CRITICAL] God Class (C3)
- **File:** `src/AppManager.js:1-141`
- **Description:** A classe `AppManager` cria o banco, define o schema/seed, registra todas as rotas, processa pagamento e cria usuário — tudo em um arquivo.
- **Impact:** Impossível testar em isolamento; qualquer mudança afeta todo o fluxo; viola SRP.
- **Recommendation:** Separar em models, services e controllers por domínio (P3).

### [CRITICAL] Hash de senha inseguro caseiro (C5)
- **File:** `src/utils.js:17-23` (`badCrypto`)
- **Description:** Senha "hasheada" por uma função caseira (loop de base64 truncado em 10 chars), usada no cadastro durante o checkout.
- **Impact:** Hash trivialmente reversível/colidível; senhas efetivamente desprotegidas.
- **Recommendation:** `crypto.scryptSync` com salt (ou bcrypt/argon2) — playbook P9.

### [HIGH] Regra de negócio dentro da rota (H1)
- **File:** `src/AppManager.js:28-78`
- **Description:** O handler de `POST /api/checkout` contém validação, criação de usuário, decisão de pagamento, matrícula, registro de pagamento e auditoria.
- **Impact:** Lógica não reutilizável nem testável; acoplada ao Express e ao driver do banco.
- **Recommendation:** Mover para `services/checkoutService` (P4).

### [HIGH] Estado global mutável (H2)
- **File:** `src/utils.js:9-10`
- **Description:** `globalCache = {}` e `totalRevenue = 0` compartilhados no módulo e mutados via `logAndCache`.
- **Impact:** Acoplamento, condições de corrida, estado imprevisível entre requisições.
- **Recommendation:** Eliminar; usar dependências injetadas e escopo por request (P6).

### [HIGH] Callback hell / pirâmide de callbacks (H4)
- **File:** `src/AppManager.js:37-77` (checkout), `src/AppManager.js:80-129` (relatório)
- **Description:** Callbacks aninhados em vários níveis; o relatório controla o término com contadores manuais `coursesPending`/`enrPending`.
- **Impact:** Ilegível, propenso a bugs de concorrência e a erros silenciosamente ignorados.
- **Recommendation:** Promisificar o driver e usar `async/await` + `Promise.all` (P10).

### [MEDIUM] Query N+1 no relatório financeiro (M1)
- **File:** `src/AppManager.js:83-127`
- **Description:** Para cada curso busca as matrículas e, para cada matrícula, uma query de usuário e outra de pagamento.
- **Impact:** Número de queries cresce com cursos×matrículas → latência.
- **Recommendation:** Carregar tudo em poucas queries e agregar em memória (P7).

### [MEDIUM] Erros engolidos (M4)
- **File:** `src/AppManager.js:57,104-106,133`
- **Description:** Callbacks ignoram o parâmetro `err` (auditoria, usuário/pagamento no relatório, deleção de usuário).
- **Impact:** Falhas passam despercebidas; respostas incorretas com status 200.
- **Recommendation:** Error handler central via `next(err)` (P5).

### [MEDIUM] Perda de integridade referencial (M5)
- **File:** `src/AppManager.js:131-137`
- **Description:** `DELETE /api/users/:id` remove apenas o usuário; a própria resposta admite que "matrículas e pagamentos ficaram sujos no banco".
- **Impact:** Dados órfãos e inconsistentes no banco.
- **Recommendation:** Remover pagamentos → matrículas → usuário em cascata (P5/service).

### [LOW] Logging via console.log (L2)
- **File:** `src/AppManager.js:45`, `src/app.js:13`, `src/utils.js:13`
- **Description:** `console.log` para logs de aplicação.
- **Impact:** Sem níveis nem estrutura.
- **Recommendation:** Logger centralizado (P12).

### [LOW] Nomenclatura de 1 letra (L3)
- **File:** `src/AppManager.js:29-33`
- **Description:** `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, id do curso e cartão.
- **Impact:** Legibilidade prejudicada.
- **Recommendation:** Nomes descritivos (P/guidelines).

## Deprecated APIs
| API | File:Line | Replace with |
|---|---|---|
| API de callbacks do driver `sqlite3` | `src/AppManager.js:37-77,83-127` | `util.promisify` + `async/await` (helpers `run/get/all`) |

## Refactoring plan (preview da Fase 3)
- P1 → `src/config/settings.js` via env; remoção do log de cartão/segredo.
- P3 → models (`user/course/enrollment/payment/audit`) + services + controllers.
- P9 → `passwordService` com scrypt+salt substitui `badCrypto`.
- P10 → `database/connection.js` promisifica o driver; checkout e relatório em async/await.
- P7 → relatório financeiro em 4 queries agregadas em memória (fim do N+1).
- P5 → `middlewares/errorHandler.js` + `HttpError`; controllers usam `next(err)`.
- M5 → `userService.deleteUser` remove pagamentos/matrículas/usuário em cascata.
- P6/P12 → fim do estado global; `logger` central substitui `console.log`.

================================
Total: 11 findings
================================
