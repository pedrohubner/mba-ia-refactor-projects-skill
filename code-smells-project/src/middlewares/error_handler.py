"""Tratamento de erro centralizado (finding M4 / playbook P5).

Substitui os blocos try/except repetidos em cada handler por um único ponto
que converte erros de domínio e inesperados no formato de resposta padronizado.
"""
import logging

from flask import jsonify

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

    @app.errorhandler(404)
    def _handle_not_found(error):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        logger.exception("Erro inesperado")
        return jsonify({"erro": "Erro interno", "sucesso": False}), 500
