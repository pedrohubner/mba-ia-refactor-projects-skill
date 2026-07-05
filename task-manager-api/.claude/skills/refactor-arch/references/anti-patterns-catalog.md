# Referência — Catálogo de Anti-Patterns (Fase 2)

Catálogo agnóstico de tecnologia. Cada entrada tem: **severidade**, **sinais de
detecção acionáveis** (o que grepar/procurar) e **por que importa**. Use a
escala de severidade abaixo, alinhada a MVC + SOLID.

## Escala de severidade

- **CRITICAL** — falha grave de arquitetura/segurança: quebra funcionamento,
  expõe dados sensíveis (credenciais hardcoded, SQL Injection) ou viola
  totalmente a separação de responsabilidades (God Class com DB + lógica +
  roteamento).
- **HIGH** — forte violação de MVC/SOLID que trava manutenção e testes: regra de
  negócio pesada dentro de controllers, acoplamento forte sem injeção de
  dependência, estado global mutável.
- **MEDIUM** — padronização, duplicação, performance moderada: N+1, middleware
  inadequado, validações ausentes nas rotas.
- **LOW** — legibilidade: nomes ruins, magic numbers, código morto, logging com
  `print`/`console.log`.

---

## CRITICAL

### C1 — Hardcoded Credentials / Secrets
**Sinais:** `SECRET_KEY = "..."`, `password = "..."`, `api_key`/`paymentGatewayKey`
/`token` com string literal, senhas de SMTP/DB no código; segredo exposto em
resposta de endpoint (ex: `secret_key` num `/health`).
**Por quê:** vazamento de credencial → comprometimento total. Segredos devem vir
de variáveis de ambiente / config externa.

### C2 — SQL Injection (concatenação de string em query)
**Sinais:** `"SELECT ... " + variavel`, f-strings/`format` montando SQL,
`execute("... %s" % x)`, `LIKE '%" + termo + "%'`. Qualquer entrada do usuário
concatenada em SQL.
**Por quê:** permite ler/alterar/apagar o banco. Correção: **queries
parametrizadas** (`?`/`%s`/binds do ORM).

### C3 — God Class / God Method / God File
**Sinais:** um único arquivo/classe concentra acesso a dados + regra de negócio +
validação + roteamento para múltiplos domínios; arquivos com centenas de linhas;
uma classe "Manager"/"Helper" que faz tudo (ex: `AppManager`, `models.py` com 4
domínios).
**Por quê:** impossível testar em isolamento; qualquer mudança afeta tudo.
Correção: separar por domínio em models/controllers/services.

### C4 — Endpoint perigoso / execução arbitrária
**Sinais:** rota que executa SQL/comando arbitrário vindo do body
(`/admin/query` com `execute(request sql)`), reset destrutivo sem auth
(`/admin/reset-db`), `eval`/`exec` de input.
**Por quê:** RCE/SQL arbitrário e destruição de dados. Correção: remover ou
proteger com autenticação e allowlist.

### C5 — Criptografia/Hash de senha inseguro ou ausente
**Sinais:** senha salva em **texto puro**; `md5(...)`/`sha1(...)` para senha;
"badCrypto" caseiro; comparação de senha em texto puro.
**Por quê:** vazamento do banco expõe senhas. Correção: `bcrypt`/`argon2`/`scrypt`
com salt.

---

## HIGH

### H1 — Business Logic no Controller / Camada errada
**Sinais:** controller/rota fazendo cálculo de negócio, montagem de SQL, regras
de desconto, orquestração de várias entidades; handler HTTP com dezenas de
linhas de lógica.
**Por quê:** viola MVC (controller deve só orquestrar). Correção: mover para
service/model.

### H2 — Estado global mutável
**Sinais:** conexão de DB em variável global (`db_connection = None` no módulo),
`globalCache = {}`, `totalRevenue = 0` compartilhado, singletons mutáveis.
**Por quê:** acoplamento forte, condições de corrida, impossível testar/paralelizar.
Correção: injeção de dependência, escopo por request, factory.

### H3 — Ausência de Injeção de Dependência / acoplamento forte
**Sinais:** módulos importando diretamente implementações concretas de acesso a
dados; `import models`/`require('./db')` no meio do controller; impossível
substituir o DB por um mock.
**Por quê:** dificulta teste e troca de implementação (DIP do SOLID). Correção:
injetar repositórios/serviços.

### H4 — Callback Hell / Pyramid of Doom / lógica assíncrona aninhada
**Sinais:** callbacks aninhados em vários níveis, controle manual de "pending
counters" para saber quando terminou (ex: relatório que decrementa contadores em
callbacks), tratamento de erro repetido em cada nível.
**Por quê:** ilegível, propenso a bugs de concorrência e a erros engolidos.
Correção: `async/await` + Promises (ou equivalente), agregação declarativa.

### H5 — Business logic no Model (Fat Model) / responsabilidade trocada
**Sinais:** model de ORM com serialização, formatação, validação e regra de
negócio dentro; método `to_dict` vazando campos sensíveis (ex: `password`).
**Por quê:** mistura persistência com regra e apresentação. Correção: mover
validação/serialização para camada apropriada; nunca serializar senha.

---

## MEDIUM

### M1 — Query N+1
**Sinais:** query dentro de loop `for`/`forEach` (buscar itens do pedido e, para
cada item, buscar o produto); `.get(id)` dentro de iteração sobre uma lista.
**Por quê:** explosão de queries → latência. Correção: JOIN, `IN (...)`,
eager loading (`joinedload`), ou uma query agregada.

### M2 — Validação ausente ou inconsistente nas rotas
**Sinais:** rota que não valida tipos/obrigatoriedade; validação duplicada e
divergente entre create/update; conversão de tipo sem try/except.
**Por quê:** entradas inválidas chegam ao banco; comportamento imprevisível.
Correção: schema de validação centralizado (marshmallow/pydantic/Joi) ou
função única de validação.

### M3 — Código duplicado (DRY)
**Sinais:** blocos de serialização/validação/cálculo copiados em vários lugares
(ex: bloco `overdue` repetido em 3 rotas; `to_dict` reimplementado inline).
**Por quê:** manutenção multiplicada, divergência silenciosa. Correção: extrair
função/método único.

### M4 — Tratamento de erro engolido / genérico
**Sinais:** `except:`/`except Exception` que retorna genérico sem logar;
`catch(err){}` vazio; erro convertido em resposta 200; ignorar `err` de callback.
**Por quê:** mascara falhas, dificulta diagnóstico. Correção: error handler
centralizado (middleware), logar com contexto, propagar status correto.

### M5 — Integridade referencial / operação não transacional
**Sinais:** deletar entidade pai sem tratar filhos ("matrículas e pagamentos
ficaram sujos"); múltiplos INSERT/UPDATE relacionados sem transação/rollback.
**Por quê:** dados órfãos e inconsistentes. Correção: cascata explícita +
transação atômica.

---

## LOW

### L1 — Magic numbers / strings mágicas
**Sinais:** `if faturamento > 10000`, `0.1`, `priority <= 2`, faixas de status
como literais espalhados.
**Por quê:** intenção obscura, mudança arriscada. Correção: constantes nomeadas.

### L2 — Logging com print/console.log
**Sinais:** `print("...")`, `console.log(...)` para log de aplicação;
"ENVIANDO EMAIL"/"ENVIANDO SMS" via print simulando efeito colateral.
**Por quê:** sem níveis, sem estrutura, polui stdout. Correção: logger real
(`logging`, `winston`/`pino`).

### L3 — Nomenclatura ruim / variáveis de 1 letra
**Sinais:** `u`, `e`, `p`, `cc`, `cid`, `td`, `c`; nomes que não revelam intenção.
**Por quê:** legibilidade. Correção: nomes descritivos.

### L4 — Imports não utilizados / código morto
**Sinais:** `import os, sys, json, datetime` sem uso; funções nunca chamadas;
`import` redundante.
**Por quê:** ruído, falsa impressão de dependência. Correção: remover.

### L5 — Configuração/flags inseguras por padrão
**Sinais:** `DEBUG = True` fixo, `app.run(debug=True)` em código de produção,
`host="0.0.0.0"` sem controle.
**Por quê:** debug em produção expõe stack traces e console interativo.
Correção: flag por ambiente (env var).

---

## Detecção de APIs DEPRECATED (obrigatória)

Sempre rode esta checagem e reporte com a severidade indicada. Recomende o
**equivalente moderno**.

| API deprecated | Onde aparece | Substituir por | Severidade |
|---|---|---|---|
| `datetime.utcnow()` | Python 3.12+ deprecou | `datetime.now(datetime.UTC)` | LOW→MEDIUM |
| `Query.get(id)` (SQLAlchemy legado) | `Model.query.get(id)` | `db.session.get(Model, id)` (SQLAlchemy 2.x) | MEDIUM |
| `Model.query` (Flask-SQLAlchemy legado) | `X.query.all()` | `db.session.execute(db.select(X))` | LOW→MEDIUM |
| `hashlib.md5`/`sha1` p/ senha | hashing de senha | `bcrypt`/`argon2` | CRITICAL (ver C5) |
| `crypto.createCipher` (Node) | criptografia | `crypto.createCipheriv` | HIGH |
| `new Buffer(...)` (Node) | buffers | `Buffer.from(...)` | MEDIUM |
| `url.parse` (Node legado) | parsing de URL | `new URL(...)` | LOW |
| `request` (npm, deprecated) | HTTP client | `fetch`/`axios`/`undici` | MEDIUM |
| Callbacks de driver sem Promise | sqlite3/mysql callback API | wrapper `promisify`/driver async | MEDIUM |

**Como detectar:** grep pelos identificadores acima + confira a versão do
runtime/framework no manifesto para saber se já está deprecado naquela versão.
