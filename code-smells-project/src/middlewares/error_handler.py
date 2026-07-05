"""Tratamento de erro centralizado (finding M4 / playbook P5).

Substitui os blocos try/except repetidos em cada handler por um único ponto
que converte erros de domínio e inesperados no formato de resposta padronizado.
"""
import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class DomainError(Exception):
    """Erro de regra de negócio com status HTTP associado."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def _handle_domain(error):
        return jsonify({"erro": str(error), "sucesso": False}), error.status

    @app.errorhandler(HTTPException)
    def _handle_http(error):
        # Preserva o status HTTP correto (404, 405, ...) em vez de virar 500.
        return jsonify({"erro": error.description, "sucesso": False}), error.code

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
