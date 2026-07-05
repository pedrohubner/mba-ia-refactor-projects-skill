"""Model de Pedido — acesso a dados de pedidos e itens.

- SQL parametrizado (C2).
- N+1 resolvido: os itens de vários pedidos são carregados com um único JOIN
  (finding M1 / playbook P7), em vez de uma query por item dentro de loops.
"""


class PedidoModel:
    def __init__(self, db):
        self.db = db

    # --- leitura de produtos usada pela regra de criação de pedido ---
    def get_produto(self, produto_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        return cur.fetchone()

    def _itens_por_pedidos(self, pedido_ids):
        """Carrega os itens de todos os pedidos de uma vez (evita N+1)."""
        if not pedido_ids:
            return {}
        placeholders = ",".join("?" * len(pedido_ids))
        cur = self.db.cursor()
        cur.execute(
            f"""
            SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
                   p.nome AS produto_nome
            FROM itens_pedido ip
            LEFT JOIN produtos p ON p.id = ip.produto_id
            WHERE ip.pedido_id IN ({placeholders})
            """,
            pedido_ids,
        )
        agrupado = {}
        for r in cur.fetchall():
            agrupado.setdefault(r["pedido_id"], []).append(
                {
                    "produto_id": r["produto_id"],
                    "produto_nome": r["produto_nome"] or "Desconhecido",
                    "quantidade": r["quantidade"],
                    "preco_unitario": r["preco_unitario"],
                }
            )
        return agrupado

    def _montar_pedidos(self, rows):
        pedido_ids = [r["id"] for r in rows]
        itens_map = self._itens_por_pedidos(pedido_ids)
        pedidos = []
        for r in rows:
            pedidos.append(
                {
                    "id": r["id"],
                    "usuario_id": r["usuario_id"],
                    "status": r["status"],
                    "total": r["total"],
                    "criado_em": r["criado_em"],
                    "itens": itens_map.get(r["id"], []),
                }
            )
        return pedidos

    def get_by_user(self, usuario_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
        return self._montar_pedidos(cur.fetchall())

    def get_all(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM pedidos")
        return self._montar_pedidos(cur.fetchall())

    def create(self, usuario_id, total, itens_calculados):
        """Cria pedido + itens e baixa estoque numa única transação (M5)."""
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cur.lastrowid
        for item in itens_calculados:
            cur.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, "
                "preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco"]),
            )
            cur.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )
        self.db.commit()
        return pedido_id

    def update_status(self, pedido_id, novo_status):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )
        self.db.commit()
        return True

    # --- agregações para o relatório (mantém a query no model) ---
    def contar_por_status(self, status):
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM pedidos WHERE status = ?", (status,))
        return cur.fetchone()[0]

    def contar_todos(self):
        cur = self.db.cursor()
        cur.execute("SELECT COUNT(*) FROM pedidos")
        return cur.fetchone()[0]

    def faturamento_total(self):
        cur = self.db.cursor()
        cur.execute("SELECT SUM(total) FROM pedidos")
        return cur.fetchone()[0] or 0
