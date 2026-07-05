# Referência — Análise de Projeto (Fase 1)

Heurísticas para descobrir a stack **sem presumir**. Sempre confirme pela
combinação de *extensões de arquivo* + *manifesto de dependências* + *imports*.

## 1. Detecção de linguagem

| Sinal | Linguagem |
|---|---|
| `.py`, `requirements.txt`, `pyproject.toml`, `Pipfile` | Python |
| `.js`/`.mjs`/`.cjs`, `package.json` | JavaScript / Node.js |
| `.ts`, `tsconfig.json` | TypeScript |
| `.go`, `go.mod` | Go |
| `.rb`, `Gemfile` | Ruby |
| `.php`, `composer.json` | PHP |
| `.java`, `pom.xml`/`build.gradle` | Java |

Se houver mistura, a linguagem principal é a do manifesto na raiz + a maioria
dos arquivos-fonte.

## 2. Detecção de framework (e versão)

Leia o manifesto de dependências e cruze com os `import`/`require` no código.

| Ecossistema | Onde ler | Frameworks comuns e como reconhecer |
|---|---|---|
| Python | `requirements.txt`, `pyproject.toml` | **Flask** (`from flask import Flask`), **FastAPI** (`from fastapi import`), **Django** (`manage.py`, `settings.py`), **SQLAlchemy** (`flask_sqlalchemy`/`sqlalchemy`) |
| Node.js | `package.json` (`dependencies`) | **Express** (`require('express')`), **NestJS** (`@nestjs/*`), **Koa**, **Fastify** |

A **versão** vem do manifesto (ex: `flask==3.1.1`, `"express": "^4.18.2"`).
Se estiver com faixa (`^`, `~`), reporte a faixa declarada.

## 3. Detecção de banco de dados

| Sinal no código/deps | Banco / camada de acesso |
|---|---|
| `sqlite3.connect(...)`, `sqlite3.Database(...)`, `sqlite:///` | SQLite |
| `psycopg2`, `pg`, `postgres://` | PostgreSQL |
| `mysql`, `mysql2`, `PyMySQL` | MySQL |
| `SQLAlchemy`, `db.Model`, `db.Column` | ORM SQLAlchemy |
| `mongoose`, `pymongo` | MongoDB |
| Strings SQL cruas (`SELECT`, `INSERT`, `CREATE TABLE`) | acesso via SQL manual |

**Tabelas/entidades:** extraia de `CREATE TABLE <nome>`, de `__tablename__`, de
classes de model (`class X(db.Model)`), ou de nomes de coleções.

## 4. Detecção do domínio

Deduza o domínio a partir de:
- Nomes de **tabelas/entidades** (`produtos`, `pedidos`, `usuarios` → e-commerce;
  `courses`, `enrollments`, `payments` → LMS/educação; `tasks`, `categories` →
  gestão de tarefas).
- Nomes de **rotas** (`/checkout`, `/relatorios/vendas`, `/tasks`).
- Textos e mensagens no código.

Descreva em uma frase: *"E-commerce API (produtos, pedidos, usuários)"*.

## 5. Mapeamento da arquitetura atual

Classifique o nível de organização — isso calibra a intensidade da Fase 3:

| Nível | Sinais | Estratégia de refatoração |
|---|---|---|
| **Monolítico / desestruturado** | Tudo em 1–4 arquivos; regra de negócio, SQL, roteamento e validação misturados; "God Class"/"God Method" | Reconstrução completa em camadas MVC |
| **Parcialmente organizado** | Já existe `models/`, `routes/`, mas com regra de negócio nas rotas, sem camada de `controllers`/`services`, segredos hardcoded | Melhorias cirúrgicas: extrair controllers/services, config, corrigir smells; não recriar o que já está correto |
| **MVC saudável** | Camadas separadas, config externa, sem smells graves | Pouca ou nenhuma mudança estrutural |

## 6. Contagem de arquivos e LOC

- Conte apenas **arquivos-fonte** (exclua `node_modules/`, `.venv/`,
  `__pycache__/`, lockfiles, `.git/`, `.claude/`, assets).
- LOC aproximado = soma de linhas dos arquivos-fonte (arredonde: "~800 lines").

## 7. Como identificar os endpoints (contrato a preservar)

Antes de refatorar, **catalogue os endpoints** — eles são o contrato que a
Fase 3 deve preservar:
- Flask: `@app.route(...)`, `app.add_url_rule(...)`, `@blueprint.route(...)`.
- Express: `app.get/post/put/delete(...)`, `router.<verbo>(...)`.

Registre método HTTP + caminho + handler de cada rota. Essa lista vira o
checklist de validação da Fase 3.
