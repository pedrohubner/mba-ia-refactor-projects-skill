import logging

logger = logging.getLogger(__name__)


class NotificationService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("Notificação: pedido %s criado para usuário %s", pedido_id, usuario_id)

    def status_alterado(self, pedido_id, status):
        logger.info("Notificação: pedido %s mudou para status '%s'", pedido_id, status)
