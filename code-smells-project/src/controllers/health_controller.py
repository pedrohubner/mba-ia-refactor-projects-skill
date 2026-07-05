"""Controller de health e index. Não vaza segredos (finding C1 corrigido)."""
from flask import jsonify


class HealthController:
    def __init__(self, db):
        self.db = db

    def index(self):
        return jsonify(
            {
                "mensagem": "Bem-vindo à API da Loja",
                "versao": "1.0.0",
                "endpoints": {
                    "produtos": "/produtos",
                    "usuarios": "/usuarios",
                    "pedidos": "/pedidos",
                    "login": "/login",
                    "relatorios": "/relatorios/vendas",
                    "health": "/health",
                },
            }
        )

    def health(self):
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM produtos")
        produtos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cur.fetchone()[0]
        return (
            jsonify(
                {
                    "status": "ok",
                    "database": "connected",
                    "counts": {
                        "produtos": produtos,
                        "usuarios": usuarios,
                        "pedidos": pedidos,
                    },
                    "versao": "1.0.0",
                }
            ),
            200,
        )
