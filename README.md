# Skill de Auditoria e Refatoração Arquitetural — `refactor-arch`

Skill de IA (Claude Code) que **audita** e **refatora** qualquer codebase para o
padrão **MVC**, de forma **agnóstica de tecnologia**. Executa três fases
sequenciais — **Análise → Auditoria (com confirmação humana) → Refatoração
validada** — e foi testada em 3 projetos legados de stacks diferentes.

A skill vive em `.claude/skills/refactor-arch/` (copiada dentro dos 3 projetos) e
é invocada por `claude "/refactor-arch"`.

```
.claude/skills/refactor-arch/
├── SKILL.md                              # prompt orquestrador das 3 fases
└── references/
    ├── project-analysis.md               # heurísticas de detecção (Fase 1)
    ├── anti-patterns-catalog.md          # catálogo de anti-patterns + APIs deprecated (Fase 2)
    ├── report-template.md                # formato do relatório de auditoria (Fase 2)
    ├── architecture-guidelines.md        # regras do MVC alvo (Fase 3)
    └── refactoring-playbook.md           # 12 padrões de transformação antes/depois (Fase 3)
```

---

## A) Análise Manual

Análise manual dos 3 projetos antes de construir a skill. Severidade conforme a
escala MVC+SOLID do desafio (CRITICAL / HIGH / MEDIUM / LOW).

### Projeto 1 — `code-smells-project` (Python/Flask, e-commerce)

Monolito de 4 arquivos (~785 linhas), tudo misturado.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | SQL Injection por concatenação | `models.py` (quase todas as queries) | Banco totalmente exposto; login bypassável com `' OR '1'='1` |
| 2 | **CRITICAL** | God File multi-domínio | `models.py:1-315`, `controllers.py` | 4 domínios num arquivo → intestável, alto risco de regressão |
| 3 | **CRITICAL** | Segredo hardcoded e vazado | `app.py:7`, `controllers.py:289` | `SECRET_KEY` no código e devolvida no `/health` |
| 4 | **CRITICAL** | Endpoints perigosos | `app.py:47-78` | `/admin/query` executa SQL arbitrário; `/admin/reset-db` apaga tudo sem auth |
| 5 | **CRITICAL** | Senha em texto puro | `models.py`, `database.py` seed | Vazamento do banco expõe senhas reais |
| 6 | **HIGH** | Regra de negócio no model/controller | `models.py:133-273` | Estoque/total/desconto colados ao SQL → não testável |
| 7 | **HIGH** | Estado global mutável | `database.py:4` | Conexão global → acoplamento e problemas de concorrência |
| 8 | **HIGH** | Vazamento de senha na serialização | `models.py:79-102` | `GET /usuarios` retorna o campo `senha` |
| 9 | **MEDIUM** | Query N+1 | `models.py:187-231` | Uma query por item de cada pedido → latência |
| 10 | **MEDIUM** | Erro genérico repetido | `controllers.py` (todos handlers) | `except: str(e)` vaza detalhes e duplica código |
| 11 | **LOW** | Magic numbers | `models.py:257-262` | Faixas de desconto soltas |
| 12 | **LOW** | `print` como log / `DEBUG=True` fixo | `app.py`, `controllers.py` | Sem log estruturado; debug em produção |

### Projeto 2 — `ecommerce-api-legacy` (Node.js/Express, LMS/checkout)

3 arquivos (~180 linhas), com "God Class" e callbacks aninhados.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Credenciais hardcoded + cartão em log | `utils.js:1-7`, `AppManager.js:45` | `pk_live_...` no Git e nº de cartão no console (violação PCI) |
| 2 | **CRITICAL** | God Class | `AppManager.js:1-141` | DB + rotas + pagamento + usuário num só lugar |
| 3 | **CRITICAL** | Hash de senha caseiro inseguro | `utils.js:17-23` | `badCrypto` trivialmente quebrável |
| 4 | **HIGH** | Regra de negócio na rota | `AppManager.js:28-78` | Todo o checkout dentro do handler |
| 5 | **HIGH** | Estado global mutável | `utils.js:9-10` | `globalCache`/`totalRevenue` compartilhados |
| 6 | **HIGH** | Callback hell | `AppManager.js:37-129` | Pirâmide de callbacks + contadores manuais de "pending" |
| 7 | **MEDIUM** | Query N+1 | `AppManager.js:83-127` | Relatório: query por curso × matrícula × usuário/pagamento |
| 8 | **MEDIUM** | Erros engolidos | `AppManager.js:57,104,133` | `err` ignorado em vários callbacks |
| 9 | **MEDIUM** | Integridade referencial | `AppManager.js:131-137` | Deletar usuário deixa matrículas/pagamentos órfãos |
| 10 | **LOW** | `console.log` como log / nomes de 1 letra | `AppManager.js` | Sem log estruturado; `u/e/p/cid/cc` |

### Projeto 3 — `task-manager-api` (Python/Flask, gestão de tarefas)

Parcialmente organizado (~1150 linhas): já tem `models/`, `routes/`, `services/`,
`utils/`, mas com regra nas rotas e problemas de segurança/qualidade.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | **CRITICAL** | Credenciais hardcoded | `app.py:13`, `notification_service.py:10` | `SECRET_KEY` e senha de SMTP no código |
| 2 | **CRITICAL** | Hash de senha com MD5 | `models/user.py:29` | MD5 sem salt → quebrável por rainbow tables |
| 3 | **HIGH** | Regra/serialização nas rotas | `routes/*.py` | Rotas gigantes montando dicts e agregando dados |
| 4 | **HIGH** | Vazamento de senha | `models/user.py:16-25`, login | `to_dict()` inclui `password` |
| 5 | **MEDIUM** | Query N+1 | `task_routes.py:41-57`, `report_routes.py:53-68` | `query.get` por task/usuário em loop |
| 6 | **MEDIUM** | Lógica `overdue` duplicada | 5 locais | `Task.is_overdue` existe mas não é usado |
| 7 | **MEDIUM** | `except:` genérico | `routes/*.py` | Mascara falhas, sem log |
| 8 | **LOW** | Magic numbers / `print` / imports mortos | vários | `import os, sys, json, time` sem uso |

**APIs deprecated (projeto 3):** `datetime.utcnow()`, `Model.query.get(id)` e o
padrão `Model.query` do Flask-SQLAlchemy legado.

---

## B) Construção da Skill

### Decisões de design

- **SKILL.md como orquestrador enxuto + conhecimento nos references.** O
  `SKILL.md` diz *o que fazer e em que ordem* (as 3 fases e os guard rails); os
  5 arquivos de referência carregam o *conhecimento de domínio* e são lidos sob
  demanda por fase. Isso mantém o prompt principal curto e o conhecimento
  reutilizável/versionável.
- **5 arquivos de referência = as 5 áreas obrigatórias:** análise de projeto,
  catálogo de anti-patterns, template de relatório, guidelines de arquitetura e
  playbook de refatoração.
- **Confirmação humana obrigatória** ao fim da Fase 2 (a fase é *read-only*):
  nada é modificado antes de um `y`.
- **Rastreabilidade finding → correção:** cada anti-pattern tem um código
  (`C2`, `H1`, `M4`, `L1`…) e cada padrão do playbook um código (`P1`…`P12`); o
  relatório cruza os dois no "Refactoring plan".

### Anti-patterns incluídos e por quê

O catálogo tem **17 anti-patterns** distribuídos por severidade (5 CRITICAL, 5
HIGH, 5 MEDIUM, 5 LOW — bem acima do mínimo de 8) mais uma seção dedicada de
**APIs deprecated**. Foram escolhidos por serem exatamente os que aparecem em
projetos legados reais e cobrirem MVC + SOLID + segurança:

- **CRITICAL:** SQL Injection, God Class, credenciais hardcoded, endpoints
  perigosos, hash de senha inseguro — falhas que quebram segurança/arquitetura.
- **HIGH:** regra de negócio na camada errada, estado global mutável, ausência
  de DI, callback hell, vazamento de dado sensível — violam MVC/SOLID e travam
  testabilidade.
- **MEDIUM:** N+1, validação ausente, duplicação, erro engolido, integridade
  referencial — qualidade/performance.
- **LOW:** magic numbers, `print` como log, nomes ruins, imports mortos, flags
  inseguras.

O **playbook** traz **12 transformações** com exemplos antes/depois (mínimo era
8), incluindo a troca de APIs deprecated (P8).

### Como garanti que é agnóstica de tecnologia

- Os **sinais de detecção** são descritos por *padrão de código* ("query SQL
  dentro de loop", "callback aninhado com contador de pending"), não por sintaxe
  de uma linguagem específica.
- A Fase 1 **descobre** a stack pelo manifesto (`requirements.txt` /
  `package.json`) em vez de presumir.
- Os exemplos do playbook aparecem **em Python e em Node.js** lado a lado.
- As guidelines definem MVC por **responsabilidade de camada**, mapeável a
  qualquer framework (a "View" de uma API é a camada de rotas).
- **Prova prática:** a mesma pasta `.claude/skills/refactor-arch/` foi copiada
  sem alteração nos 3 projetos e funcionou nos 3.

### Desafios encontrados e como resolvi

- **Preservar o contrato vs. corrigir segurança.** Endpoints como `/admin/query`
  (SQL arbitrário) não têm como ficar seguros; a guideline autoriza remover
  findings CRITICAL desde que documentado — foi o que fiz (removido e registrado
  no relatório).
- **`datetime.utcnow()` deprecated vs. datas naive no banco.** Trocar por
  `datetime.now(timezone.utc)` gera datetime *aware*, incompatível com as colunas
  naive já persistidas. Resolvi com um helper `now_utc()` que usa a API moderna
  mas devolve valor naive — remove o deprecated sem quebrar comparações.
- **Sem dependências novas na validação.** Em vez de `bcrypt`, usei `PBKDF2`
  (Python) e `scrypt` (Node), ambos da biblioteca padrão — hash seguro sem
  alterar `requirements.txt`/`package.json`.
- **Projeto parcialmente organizado (nº 3).** A skill precisa *calibrar* a
  intervenção: aqui foi cirúrgica (adicionar `config/`, `controllers/`,
  `middlewares/` e mover a regra das rotas), sem recriar `models/`/`routes/` que
  já existiam.

---

## C) Resultados

### Resumo dos relatórios de auditoria

| Projeto | Stack | Arquivos | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python/Flask | 4 | 5 | 5 | 4 | 3 | **17** |
| 2 — ecommerce-api-legacy | Node.js/Express | 3 | 3 | 3 | 3 | 2 | **11** |
| 3 — task-manager-api | Python/Flask | 15 | 2 | 2 | 3 | 3 | **10** |

Relatórios completos em [`reports/`](reports/).

### Antes / depois da estrutura

**Projeto 1** — monolito → MVC completo:

```
ANTES                          DEPOIS
app.py (rotas+admin)           app.py (entry point)
controllers.py (tudo)          src/
models.py (4 domínios)         ├── config/settings.py
database.py (conexão global)   ├── database/connection.py
                               ├── models/{produto,usuario,pedido}_model.py
                               ├── services/{pedido,relatorio,notification}_service.py
                               ├── controllers/{produto,usuario,pedido,health}_controller.py
                               ├── views/routes.py
                               ├── middlewares/error_handler.py
                               └── app.py (composition root)
```

**Projeto 2** — God Class → MVC + async/await:

```
ANTES                          DEPOIS
src/app.js                     src/
src/AppManager.js (God Class)  ├── config/settings.js
src/utils.js (segredos/global) ├── database/connection.js (promisificado)
                               ├── models/{user,course,enrollment,payment,audit}Model.js
                               ├── services/{checkout,report,user,payment,password}Service.js
                               ├── controllers/{checkout,report,user}Controller.js
                               ├── middlewares/{errorHandler,logger}.js
                               ├── views/routes.js
                               └── app.js (composition root)
```

**Projeto 3** — parcial → camadas completas:

```
ANTES                          DEPOIS (+ camadas adicionadas)
app.py (config inline)         + config/settings.py
models/ (md5, leak)            + controllers/{task,user,report}_controller.py
routes/ (regra + N+1)          + middlewares/error_handler.py
services/notification (segredo)  services/ (task,user,report,category + notification saneado)
utils/helpers (imports mortos)   routes/ (agora finas, delegam a controllers)
                                 models/ (PBKDF2, sem leak, sem utcnow)
```

### Checklist de validação (preenchido para os 3 projetos)

| Item | P1 | P2 | P3 |
|---|:--:|:--:|:--:|
| **Fase 1** — linguagem detectada | ✅ | ✅ | ✅ |
| Framework detectado | ✅ | ✅ | ✅ |
| Domínio descrito corretamente | ✅ | ✅ | ✅ |
| Nº de arquivos condiz | ✅ | ✅ | ✅ |
| **Fase 2** — relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding com arquivo e linha | ✅ | ✅ | ✅ |
| Ordenado por severidade | ✅ | ✅ | ✅ |
| ≥ 5 findings | ✅ (17) | ✅ (11) | ✅ (10) |
| Detecção de APIs deprecated | ✅ (n/a) | ✅ | ✅ |
| Pausa/pede confirmação | ✅ | ✅ | ✅ |
| **Fase 3** — estrutura MVC | ✅ | ✅ | ✅ |
| Config sem hardcoded | ✅ | ✅ | ✅ |
| Models de dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ | ✅ | ✅ |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ | ✅ | ✅ |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ | ✅ | ✅ |

### Logs das aplicações rodando após a refatoração

**Projeto 1 (Flask):**
```
GET    /health          -> 200  {"counts":{"pedidos":0,"produtos":10,"usuarios":3},"database":"connected","status":"ok"}
GET    /produtos        -> 200  {"dados":[...],"sucesso":true}
POST   /login           -> 200  (senha via PBKDF2)
GET    /produtos/busca?q=' OR '1'='1  -> 200  {"dados":[],"total":0}   ← SQLi neutralizado
```

**Projeto 2 (Express):**
```
POST /api/checkout (card 4...)      -> {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (card 5...)      -> {"error":"Pagamento recusado"}
GET  /api/admin/financial-report    -> [{"course":"Clean Architecture","revenue":997,...}]
DELETE /api/users/1                 -> {"msg":"Usuário e dados relacionados removidos com sucesso"}
[INFO] Processando pagamento de 497 (cartão ****4444)   ← cartão mascarado
```

**Projeto 3 (Flask):**
```
GET  /tasks/stats   -> 200  {"total":10,"done":2,"overdue":2,"completion_rate":20.0,...}
POST /login         -> 200  (senha via PBKDF2)
GET  /users         -> 200  (sem campo "password")   ← vazamento corrigido
```

### Comportamento em stacks diferentes

A skill se comportou de forma consistente: na Fase 1 detectou corretamente
Python/Flask (P1, P3) e Node/Express (P2); na Fase 3 aplicou o **mesmo** conjunto
de camadas MVC, mas adaptando as transformações à stack (SQL parametrizado em
Python; promisify + async/await em Node) e ao nível de organização (reconstrução
total em P1/P2, melhorias cirúrgicas em P3).

---

## D) Como Executar

### Pré-requisitos

- **Claude Code** instalado e configurado.
- **Python 3.9+** (projetos 1 e 3) e **Node.js 18+** (projeto 2).

### Rodar a skill em cada projeto

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

A skill executa a Fase 1 (análise), a Fase 2 (auditoria — salva o relatório em
`reports/` e **pede confirmação**) e, após o `y`, a Fase 3 (refatoração +
validação).

### Validar que a refatoração funciona

**Projeto 1 — code-smells-project (Flask):**
```bash
cd code-smells-project
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python app.py        # sobe em http://localhost:5000
curl http://localhost:5000/health
curl http://localhost:5000/produtos
```

**Projeto 2 — ecommerce-api-legacy (Express):**
```bash
cd ecommerce-api-legacy
npm install
npm start                        # sobe em http://localhost:3000
# ver requisições em api.http
curl -X POST http://localhost:3000/api/checkout -H 'Content-Type: application/json' \
  -d '{"usr":"Ana","eml":"ana@x.com","pwd":"123","c_id":2,"card":"4111222233334444"}'
curl http://localhost:3000/api/admin/financial-report
```

**Projeto 3 — task-manager-api (Flask):**
```bash
cd task-manager-api
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
./.venv/bin/python seed.py       # popula o banco (rode antes do 1º boot)
./.venv/bin/python app.py        # sobe em http://localhost:5000
curl http://localhost:5000/tasks
curl http://localhost:5000/tasks/stats
```

Em todos os casos, a aplicação deve **iniciar sem erros** e os **endpoints
originais** devem responder normalmente.
