import os


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("1", "true", "yes")
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))

    CATEGORIAS_VALIDAS = [
        "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
    ]
    STATUS_PEDIDO_VALIDOS = [
        "pendente", "aprovado", "enviado", "entregue", "cancelado",
    ]
    NOME_MIN = 2
    NOME_MAX = 200


settings = Settings()
