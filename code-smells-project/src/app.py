import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import settings
from src.controllers.health_controller import HealthController
from src.controllers.pedido_controller import PedidoController
from src.controllers.produto_controller import ProdutoController
from src.controllers.usuario_controller import UsuarioController
from src.database.connection import create_connection
from src.middlewares.error_handler import register_error_handlers
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.services.notification_service import NotificationService
from src.services.pedido_service import PedidoService
from src.services.relatorio_service import RelatorioService
from src.views.routes import register_routes


def create_app():
    logging.basicConfig(level=logging.INFO)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    CORS(app)

    db = create_connection(settings.DB_PATH)

    produto_model = ProdutoModel(db)
    usuario_model = UsuarioModel(db)
    pedido_model = PedidoModel(db)

    notification = NotificationService()
    pedido_service = PedidoService(pedido_model, notification)
    relatorio_service = RelatorioService(pedido_model)

    controllers = {
        "produto": ProdutoController(produto_model),
        "usuario": UsuarioController(usuario_model),
        "pedido": PedidoController(
            pedido_service, relatorio_service, pedido_model, notification
        ),
        "health": HealthController(db),
    }

    register_routes(app, controllers)
    register_error_handlers(app)
    return app
