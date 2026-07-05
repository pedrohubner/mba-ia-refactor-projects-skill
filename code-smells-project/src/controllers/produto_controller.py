"""Controller de Produto — fino: valida entrada, chama o model, monta resposta.

Sem SQL, sem try/except repetido (o error handler central cuida das exceções).
"""
from flask import jsonify, request

from src.config.settings import settings
from src.middlewares.error_handler import DomainError


class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def listar(self):
        produtos = self.produto_model.get_all()
        return jsonify({"dados": produtos, "sucesso": True}), 200

    def buscar(self, id):
        produto = self.produto_model.get_by_id(id)
        if not produto:
            raise DomainError("Produto não encontrado", 404)
        return jsonify({"dados": produto, "sucesso": True}), 200

    def pesquisar(self):
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria")
        preco_min = request.args.get("preco_min", type=float)
        preco_max = request.args.get("preco_max", type=float)
        resultados = self.produto_model.search(termo, categoria, preco_min, preco_max)
        return (
            jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}),
            200,
        )

    def _validar(self, dados):
        if not dados:
            raise DomainError("Dados inválidos", 400)
        for campo in ("nome", "preco", "estoque"):
            if campo not in dados:
                raise DomainError(f"{campo.capitalize()} é obrigatório", 400)
        if dados["preco"] < 0:
            raise DomainError("Preço não pode ser negativo", 400)
        if dados["estoque"] < 0:
            raise DomainError("Estoque não pode ser negativo", 400)
        nome = dados["nome"]
        if not (settings.NOME_MIN <= len(nome) <= settings.NOME_MAX):
            raise DomainError("Nome com tamanho inválido", 400)
        categoria = dados.get("categoria", "geral")
        if categoria not in settings.CATEGORIAS_VALIDAS:
            raise DomainError(
                f"Categoria inválida. Válidas: {settings.CATEGORIAS_VALIDAS}", 400
            )

    def criar(self):
        dados = request.get_json()
        self._validar(dados)
        produto_id = self.produto_model.create(
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )
        return (
            jsonify(
                {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}
            ),
            201,
        )

    def atualizar(self, id):
        if not self.produto_model.get_by_id(id):
            raise DomainError("Produto não encontrado", 404)
        dados = request.get_json()
        self._validar(dados)
        self.produto_model.update(
            id,
            dados["nome"],
            dados.get("descricao", ""),
            dados["preco"],
            dados["estoque"],
            dados.get("categoria", "geral"),
        )
        return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200

    def deletar(self, id):
        if not self.produto_model.get_by_id(id):
            raise DomainError("Produto não encontrado", 404)
        self.produto_model.delete(id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200
