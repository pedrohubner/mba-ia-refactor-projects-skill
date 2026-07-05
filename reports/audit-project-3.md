================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0 (Flask-SQLAlchemy 3.1)
Files:   15 analyzed | ~1150 lines of code
Date:    2026-07-05

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 3 | LOW: 3
Total: 10 findings

> Projeto parcialmente organizado (já possui `models/`, `routes/`, `services/`,
> `utils/`). A refatoração é cirúrgica: adicionar as camadas ausentes
> (`config/`, `controllers/`, `middlewares/`) e corrigir os smells sem recriar o
> que já está correto.

## Findings

### [CRITICAL] Credenciais hardcoded (C1)
- **File:** `app.py:13`, `services/notification_service.py:10`
- **Description:** `SECRET_KEY = 'super-secret-key-123'` fixo no app e `email_password = 'senha123'` fixo no serviço de notificação.
- **Impact:** Segredos versionados no Git; sessões forjáveis e credencial de email exposta.
- **Recommendation:** Config via variáveis de ambiente em `config/settings.py` (playbook P1).

### [CRITICAL] Hash de senha com MD5 (C5)
- **File:** `models/user.py:29,32`
- **Description:** `set_password`/`check_password` usam `hashlib.md5` sem salt.
- **Impact:** MD5 é quebrável; vazamento do banco expõe senhas via rainbow tables.
- **Recommendation:** PBKDF2 com salt (ou bcrypt/argon2) — playbook P9.

### [HIGH] Regra de negócio e serialização dentro das rotas (H1)
- **File:** `routes/task_routes.py:11-63`, `routes/report_routes.py:12-101`, `routes/user_routes.py:10-40`
- **Description:** As rotas montam dicionários, calculam `overdue`, agregam estatísticas e orquestram tudo — sem camada de controller/service.
- **Impact:** Lógica não reutilizável nem testável; rotas gigantes; viola MVC.
- **Recommendation:** Extrair para `controllers/` (orquestração) + `services/` (regra) — P4.

### [HIGH] Vazamento de senha na serialização (H5)
- **File:** `models/user.py:16-25` (`to_dict`), `routes/user_routes.py:207-211` (login)
- **Description:** `User.to_dict()` inclui o campo `password`; o login devolve o usuário via `to_dict`.
- **Impact:** `GET /users/<id>` e `POST /login` expõem o hash da senha.
- **Recommendation:** Serializador que omite `password` (P9).

### [MEDIUM] Query N+1 (M1)
- **File:** `routes/task_routes.py:41-57`, `routes/report_routes.py:53-68`, `routes/user_routes.py:35-40`
- **Description:** `get_tasks` faz `User.query.get` e `Category.query.get` por task; o `summary_report` roda `Task.query` por usuário dentro de um loop.
- **Impact:** Número de queries cresce com o volume → latência.
- **Recommendation:** Eager loading (`joinedload`) e agregação em memória (P7).

### [MEDIUM] Lógica de `overdue` duplicada (M3)
- **File:** `routes/task_routes.py:30-39,71-80,283-288`, `routes/user_routes.py:171-181`, `routes/report_routes.py:34-43`
- **Description:** O mesmo bloco aninhado de checagem de atraso aparece em 5 lugares (e o `Task.is_overdue` existente não é usado).
- **Impact:** Divergência silenciosa; manutenção multiplicada.
- **Recommendation:** Função única `is_overdue()` reutilizada por todos (P11).

### [MEDIUM] Tratamento de erro genérico com `except:` (M4)
- **File:** `routes/task_routes.py:62,236`, `routes/report_routes.py:186-188,206-208,220-222`, `routes/user_routes.py:130-132,149-151`
- **Description:** Vários `except:`/`except Exception` capturam tudo e devolvem genérico, sem log.
- **Impact:** Mascara falhas reais; dificulta diagnóstico.
- **Recommendation:** Error handler centralizado com `DomainError` (P5).

### [LOW] Magic numbers / strings (L1)
- **File:** `routes/report_routes.py:129` (`priority <= 2`), status/prioridade literais espalhados
- **Description:** Limiares e listas de status/roles repetidos como literais.
- **Impact:** Intenção obscura, mudança arriscada.
- **Recommendation:** Constantes em `config/settings.py` (P4).

### [LOW] Logging via print (L2)
- **File:** `routes/task_routes.py:149,153,219`, `routes/user_routes.py:83,89,147`
- **Description:** `print` para logs de aplicação.
- **Impact:** Sem níveis nem estrutura.
- **Recommendation:** Módulo `logging` (P12).

### [LOW] Imports não utilizados (L4)
- **File:** `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:8`, `utils/helpers.py:2-7`
- **Description:** `import os, sys, json, time, hashlib, math` sem uso em vários arquivos.
- **Impact:** Ruído; falsa impressão de dependências.
- **Recommendation:** Remover (P12).

## Deprecated APIs
| API | File:Line | Replace with |
|---|---|---|
| `datetime.utcnow()` | `models/task.py:15-16`, `models/user.py:14`, `models/category.py:11`, `routes/*`, `seed.py` | `datetime.now(timezone.utc)` (helper `now_utc()`) |
| `Model.query.get(id)` | `routes/task_routes.py:67,158,227`, `routes/user_routes.py:29,94,135`, `routes/report_routes.py:105` | `db.session.get(Model, id)` (SQLAlchemy 2.x) |
| `Model.query` (Flask-SQLAlchemy legado) | `routes/*` (listagens/filtros) | `db.session.execute(db.select(Model))` |

## Refactoring plan (preview da Fase 3)
- P1 → `config/settings.py` via env; segredos de app e de SMTP fora do código.
- P4 → `controllers/` (task/user/report) + `services/` (task/user/report/category); rotas viram Views finas.
- P9 → `User.set_password` com PBKDF2+salt; `to_dict` omite `password`.
- P7 → `list_tasks` com `joinedload`; relatório agrega tasks em memória.
- P11 → `utils.helpers.is_overdue` único; `Task.is_overdue` delega a ele.
- P5 → `middlewares/error_handler.py` com `DomainError`; fim dos `except:`.
- P8 → `now_utc()` substitui `utcnow()`; `db.session.get` substitui `query.get`.
- P12 → `logging` no lugar de `print`; imports mortos removidos.

================================
Total: 10 findings
================================
