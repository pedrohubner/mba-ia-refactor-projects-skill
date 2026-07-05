from src.middlewares.error_handler import DomainError


class PedidoService:
    def __init__(self, pedido_model, notification_service):
        self.pedido_model = pedido_model
        self.notification = notification_service

    def criar(self, usuario_id, itens):
        if not itens:
            raise DomainError("Pedido deve ter pelo menos 1 item", 400)

        total = 0.0
        itens_calculados = []
        for item in itens:
            produto = self.pedido_model.get_produto(item["produto_id"])
            if produto is None:
                raise DomainError(
                    f"Produto {item['produto_id']} não encontrado", 400
                )
            if produto["estoque"] < item["quantidade"]:
                raise DomainError(
                    f"Estoque insuficiente para {produto['nome']}", 400
                )
            total += produto["preco"] * item["quantidade"]
            itens_calculados.append(
                {
                    "produto_id": item["produto_id"],
                    "quantidade": item["quantidade"],
                    "preco": produto["preco"],
                }
            )

        pedido_id = self.pedido_model.create(usuario_id, total, itens_calculados)
        self.notification.pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}
