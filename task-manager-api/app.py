"""Composition root / entry point (application factory).

Lê a config de env (sem segredos hardcoded), inicializa o db, registra os
blueprints (View) e o error handler central, e expõe `create_app()`.
"""
import logging

from flask import jsonify
from flask_cors import CORS

from config.settings import settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from utils.helpers import now_utc


def create_app():
    logging.basicConfig(level=logging.INFO)
    from flask import Flask

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    app.config['SECRET_KEY'] = settings.SECRET_KEY

    CORS(app)
    db.init_app(app)

    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(now_utc())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    register_error_handlers(app)

    with app.app_context():
        # Garante que os models estão importados antes do create_all.
        from models import task, user, category  # noqa: F401
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=settings.DEBUG, host=settings.HOST, port=settings.PORT)
