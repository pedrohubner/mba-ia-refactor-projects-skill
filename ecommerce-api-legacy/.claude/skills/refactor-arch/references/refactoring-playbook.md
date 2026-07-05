# Referência — Playbook de Refatoração (Fase 3)

Padrões concretos de transformação, um por família de anti-pattern, com exemplos
**antes/depois**. Os exemplos usam Python/Flask e Node.js/Express para reforçar
que os padrões são agnósticos — aplique o equivalente na stack detectada.

---

## P1 — Extrair segredos/config para módulo de configuração (corrige C1, L5)

**Antes (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```
**Depois (`config/settings.py`):**
```python
import os
class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
settings = Settings()
```
**Antes (Node):** `const config = { paymentGatewayKey: "pk_live_..." }`
**Depois (`config/settings.js`):**
```js
module.exports = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  port: Number(process.env.PORT) || 3000,
};
```

---

## P2 — Parametrizar SQL (corrige C2 SQL Injection)

**Antes:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("... WHERE email = '" + email + "' AND senha = '" + senha + "'")
```
**Depois:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```
Para filtros dinâmicos, monte a cláusula com placeholders e uma lista de params:
```python
clauses, params = ["1=1"], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)"); params += [f"%{termo}%", f"%{termo}%"]
if categoria:
    clauses.append("categoria = ?"); params.append(categoria)
cursor.execute("SELECT * FROM produtos WHERE " + " AND ".join(clauses), params)
```

---

## P3 — Quebrar God Class/God File por domínio (corrige C3)

**Antes:** `models.py` (350 linhas) com produtos + usuários + pedidos +
relatórios; ou `AppManager.js` com DB + rotas + pagamento.

**Depois:** um model por entidade, um controller por domínio:
```
models/produto_model.py     -> ProdutoModel: get_all/get_by_id/create/update/delete/search
models/usuario_model.py     -> UsuarioModel: get_all/get_by_id/create/find_by_credentials
models/pedido_model.py      -> PedidoModel: create/get_by_user/get_all/update_status
controllers/produto_controller.py
controllers/pedido_controller.py
services/relatorio_service.py  -> regra de faturamento/desconto
```
Cada classe recebe a conexão/So no construtor (ver P6, injeção).

---

## P4 — Mover regra de negócio do Controller/Route para Service/Model (corrige H1, H5)

**Antes (controller com regra de desconto e cálculo de total):**
```python
def relatorio_vendas():
    ...
    if faturamento > 10000: desconto = faturamento * 0.1
    elif faturamento > 5000: desconto = faturamento * 0.05
    ...
```
**Depois (`services/relatorio_service.py`):**
```python
DESCONTO_FAIXAS = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]  # elimina magic numbers (L1)
def calcular_desconto(faturamento):
    for limite, taxa in DESCONTO_FAIXAS:
        if faturamento > limite:
            return round(faturamento * taxa, 2)
    return 0.0
```
Controller só chama `relatorio_service.gerar()` e devolve JSON.

---

## P5 — Centralizar tratamento de erro (corrige M4, remove try/except repetido)

**Antes:** cada handler tem `try/except Exception: return jsonify({"erro": str(e)}), 500`.

**Depois (`middlewares/error_handler.py`, Flask):**
```python
from flask import jsonify
class DomainError(Exception):
    def __init__(self, message, status=400): super().__init__(message); self.status = status
def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def _domain(e): return jsonify({"erro": str(e), "sucesso": False}), e.status
    @app.errorhandler(Exception)
    def _unexpected(e):
        app.logger.exception("erro inesperado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
```
Controllers ficam limpos: levantam `DomainError("Produto não encontrado", 404)`.

> **Cuidado (Flask):** registre também um handler para `werkzeug.exceptions.HTTPException`
> **antes** do handler genérico de `Exception`; senão erros de roteamento (404/405)
> caem no handler de `Exception` e viram 500. Ex:
> `@app.errorhandler(HTTPException) def _h(e): return jsonify({"erro": e.description}), e.code`

**Express:** `app.use((err, req, res, next) => res.status(err.status||500).json({error: err.message}))`.

---

## P6 — Eliminar estado global mutável via injeção de dependência (corrige H2, H3)

**Antes:** `db_connection = None` global; `globalCache = {}`; `import models` no controller.

**Depois:** factory de conexão + injeção no construtor:
```python
# models/produto_model.py
class ProdutoModel:
    def __init__(self, db): self.db = db          # dependência injetada
    def get_all(self):
        cur = self.db.cursor(); cur.execute("SELECT * FROM produtos"); ...
# app.py (composition root)
db = get_connection(settings.DB_PATH)
produto_model = ProdutoModel(db)
produto_controller = ProdutoController(produto_model)
```
Testes podem injetar um DB fake. Nada global mutável.

---

## P7 — Resolver Query N+1 (corrige M1)

**Antes:**
```python
for row in pedidos:
    cursor.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in itens:
        cursor.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```
**Depois (uma query com JOIN, parametrizada):**
```python
cursor.execute("""
    SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, p.nome
    FROM itens_pedido ip JOIN produtos p ON p.id = ip.produto_id
    WHERE ip.pedido_id IN (%s)
""" % ",".join("?"*len(ids)), ids)
```
**ORM (SQLAlchemy):** trocar loop `User.query.get(id)` por `joinedload`:
```python
tasks = db.session.execute(
    db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
).scalars().all()
```

---

## P8 — Substituir APIs deprecated pelo equivalente moderno (corrige seção Deprecated)

| Antes | Depois |
|---|---|
| `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `Model.query.get(id)` | `db.session.get(Model, id)` |
| `Model.query.all()` | `db.session.execute(db.select(Model)).scalars().all()` |
| `hashlib.md5(pwd)` | `bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())` |
| `new Buffer(x)` | `Buffer.from(x)` |
| callback do `sqlite3` | `util.promisify` + `async/await` |

---

## P9 — Hash de senha seguro (corrige C5)

**Antes:** `self.password = hashlib.md5(pwd.encode()).hexdigest()` /
`badCrypto(pwd)` caseiro / senha em texto puro.
**Depois:**
```python
import bcrypt
def set_password(self, pwd): self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
def check_password(self, pwd): return bcrypt.checkpw(pwd.encode(), self.password.encode())
```
> Se adicionar `bcrypt` for inviável no ambiente de validação, no mínimo use
> `hashlib.pbkdf2_hmac` (stdlib, com salt) e **nunca** exponha a senha em
> respostas (`to_dict` deve omitir `password`).

---

## P10 — Callback Hell → async/await (corrige H4)

**Antes (Express + sqlite3 com callbacks aninhados e pending counters):**
```js
this.db.get("...", [cid], (err, course) => {
  this.db.get("...", [e], (err, user) => {
    this.db.run("...", [...], function(err) { /* ... */ });
  });
});
```
**Depois (promisificar o driver e usar async/await):**
```js
const { promisify } = require('util');
const get = promisify(db.get.bind(db)), run = promisify(db.run.bind(db)), all = promisify(db.all.bind(db));
async function checkout(req, res, next) {
  try {
    const course = await get("SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
    if (!course) throw new HttpError(404, "Curso não encontrado");
    // ... fluxo linear, sem pirâmide
  } catch (err) { next(err); }
}
```
O relatório financeiro (contadores manuais de "pending") vira `await Promise.all(...)`.

---

## P11 — Extrair validação e eliminar duplicação (corrige M2, M3, DRY)

Centralize regras repetidas (ex: bloco `overdue`, validação de status/prioridade)
numa função/schema único:
```python
def is_overdue(task):
    return bool(task.due_date and task.due_date < now_utc()
                and task.status not in ("done", "cancelled"))
```
Use um schema (marshmallow/pydantic/Joi) para validar payloads em vez de `if`s
espalhados e divergentes entre create/update.

---

## P12 — Trocar print/console.log por logger + remover código morto (corrige L2, L4)

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Produto criado id=%s", produto_id)   # em vez de print(...)
```
Remova imports não usados (`import os, sys, json` sem uso) e funções mortas.
Efeitos colaterais simulados por `print("ENVIANDO EMAIL...")` viram chamadas a um
`notification_service` (mesmo que stub), isolando o efeito.

---

## Checklist de saída da Fase 3

- [ ] `config/` sem segredos hardcoded (tudo via env)
- [ ] Models por domínio, SQL parametrizado, sem estado global
- [ ] Controllers finos; regra de negócio em services/models
- [ ] Routes/Views só roteiam
- [ ] Error handler centralizado
- [ ] N+1 resolvido; APIs deprecated trocadas
- [ ] Entry point/composition root claro
- [ ] App **sobe** e **todos os endpoints originais respondem**
