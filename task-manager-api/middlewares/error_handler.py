import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class DomainError(Exception):

    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def register_error_handlers(app):
    @app.errorhandler(DomainError)
    def _handle_domain(error):
        return jsonify({'error': str(error)}), error.status

    @app.errorhandler(HTTPException)
    def _handle_http(error):
        return jsonify({'error': error.description}), error.code

    @app.errorhandler(Exception)
    def _handle_unexpected(error):
        logger.exception('Erro inesperado')
        return jsonify({'error': 'Erro interno'}), 500
