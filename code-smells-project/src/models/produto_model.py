def _row_to_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM produtos")
        return [_row_to_dict(r) for r in cur.fetchall()]

    def get_by_id(self, produto_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
        row = cur.fetchone()
        return _row_to_dict(row) if row else None

    def create(self, nome, descricao, preco, estoque, categoria):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        self.db.commit()
        return cur.lastrowid

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        cur = self.db.cursor()
        cur.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        self.db.commit()
        return True

    def delete(self, produto_id):
        cur = self.db.cursor()
        cur.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        self.db.commit()
        return True

    def search(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        clauses, params = ["1=1"], []
        if termo:
            clauses.append("(nome LIKE ? OR descricao LIKE ?)")
            params += [f"%{termo}%", f"%{termo}%"]
        if categoria:
            clauses.append("categoria = ?")
            params.append(categoria)
        if preco_min is not None:
            clauses.append("preco >= ?")
            params.append(preco_min)
        if preco_max is not None:
            clauses.append("preco <= ?")
            params.append(preco_max)
        cur = self.db.cursor()
        cur.execute("SELECT * FROM produtos WHERE " + " AND ".join(clauses), params)
        return [_row_to_dict(r) for r in cur.fetchall()]
