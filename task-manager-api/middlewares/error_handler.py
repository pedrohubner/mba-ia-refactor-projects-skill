"""Tratamento de erro centralizado (findings M4 / playbook P5).

Substitui os `except:`/`except Exception` genéricos espalhados pelas rotas por um
único ponto que converte erros de domínio e inesperados no formato padronizado.
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
        return jsonify({'error': str(error)}), error.status

    @app.errorhandler(404)
    def _handle_not_found(error):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        logger.exception('Erro inesperado')
        return jsonify({'error': 'Erro interno'}), 500
