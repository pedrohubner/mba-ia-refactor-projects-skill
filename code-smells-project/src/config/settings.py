"""Configuração central da aplicação.

Todos os segredos e flags vêm de variáveis de ambiente (P1 do playbook),
eliminando credenciais hardcoded (finding C1) e DEBUG fixo (finding L5).
"""
import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    # Constantes de domínio centralizadas (elimina magic strings/numbers - L1)
    CATEGORIAS_VALIDAS = [
        "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
    ]
    STATUS_PEDIDO_VALIDOS = [
        "pendente", "aprovado", "enviado", "entregue", "cancelado",
    ]
    NOME_MIN = 2
    NOME_MAX = 200


settings = Settings()
