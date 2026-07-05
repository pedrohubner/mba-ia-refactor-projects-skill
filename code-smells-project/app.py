"""Entry point — delega ao composition root em src/app.py.

Mantém o comando original de execução: `python app.py`.
"""
from src.app import create_app
from src.config.settings import settings

app = create_app()

if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print(f"Rodando em http://localhost:{settings.PORT}")
    print("=" * 50)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
