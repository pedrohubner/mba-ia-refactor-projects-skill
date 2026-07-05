"""Controller de Usuário — cadastro, listagem e login."""
from flask import jsonify, request

from src.middlewares.error_handler import DomainError


class UsuarioController:
    def __init__(self, usuario_model):
        self.usuario_model = usuario_model

    def listar(self):
        usuarios = self.usuario_model.get_all()
        return jsonify({"dados": usuarios, "sucesso": True}), 200

    def buscar(self, id):
        usuario = self.usuario_model.get_by_id(id)
        if not usuario:
            raise DomainError("Usuário não encontrado", 404)
        return jsonify({"dados": usuario, "sucesso": True}), 200

    def criar(self):
        dados = request.get_json()
        if not dados:
            raise DomainError("Dados inválidos", 400)
        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not nome or not email or not senha:
            raise DomainError("Nome, email e senha são obrigatórios", 400)
        usuario_id = self.usuario_model.create(nome, email, senha)
        return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201

    def login(self):
        dados = request.get_json()
        email = dados.get("email", "") if dados else ""
        senha = dados.get("senha", "") if dados else ""
        if not email or not senha:
            raise DomainError("Email e senha são obrigatórios", 400)
        usuario = self.usuario_model.authenticate(email, senha)
        if not usuario:
            raise DomainError("Email ou senha inválidos", 401)
        return (
            jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}),
            200,
        )
