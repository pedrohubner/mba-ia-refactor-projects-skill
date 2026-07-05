from flask import jsonify, request

from src.config.settings import settings
from src.middlewares.error_handler import DomainError


class PedidoController:
    def __init__(self, pedido_service, relatorio_service, pedido_model, notification):
        self.pedido_service = pedido_service
        self.relatorio_service = relatorio_service
        self.pedido_model = pedido_model
        self.notification = notification

    def criar(self):
        dados = request.get_json()
        if not dados:
            raise DomainError("Dados inválidos", 400)
        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            raise DomainError("Usuario ID é obrigatório", 400)
        resultado = self.pedido_service.criar(usuario_id, itens)
        return (
            jsonify(
                {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}
            ),
            201,
        )

    def listar_por_usuario(self, usuario_id):
        pedidos = self.pedido_model.get_by_user(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def listar_todos(self):
        pedidos = self.pedido_model.get_all()
        return jsonify({"dados": pedidos, "sucesso": True}), 200

    def atualizar_status(self, pedido_id):
        dados = request.get_json()
        novo_status = dados.get("status", "") if dados else ""
        if novo_status not in settings.STATUS_PEDIDO_VALIDOS:
            raise DomainError("Status inválido", 400)
        self.pedido_model.update_status(pedido_id, novo_status)
        self.notification.status_alterado(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200

    def relatorio_vendas(self):
        relatorio = self.relatorio_service.gerar_relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
