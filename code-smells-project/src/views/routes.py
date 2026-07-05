"""Camada View/Routes — mapeia URL + método → controller. Sem lógica de negócio.

Mantém exatamente os mesmos endpoints, métodos e nomes do projeto original
(contrato preservado). Os endpoints administrativos inseguros do original
(`/admin/query` — execução de SQL arbitrário, e `/admin/reset-db` — destruição
sem autenticação) foram REMOVIDOS por serem findings CRITICAL (C4).
"""


def register_routes(app, controllers):
    produto = controllers["produto"]
    usuario = controllers["usuario"]
    pedido = controllers["pedido"]
    health = controllers["health"]

    # Produtos
    app.add_url_rule("/produtos", "listar_produtos", produto.listar, methods=["GET"])
    app.add_url_rule("/produtos/busca", "buscar_produtos", produto.pesquisar, methods=["GET"])
    app.add_url_rule("/produtos/<int:id>", "buscar_produto", produto.buscar, methods=["GET"])
    app.add_url_rule("/produtos", "criar_produto", produto.criar, methods=["POST"])
    app.add_url_rule("/produtos/<int:id>", "atualizar_produto", produto.atualizar, methods=["PUT"])
    app.add_url_rule("/produtos/<int:id>", "deletar_produto", produto.deletar, methods=["DELETE"])

    # Usuários
    app.add_url_rule("/usuarios", "listar_usuarios", usuario.listar, methods=["GET"])
    app.add_url_rule("/usuarios/<int:id>", "buscar_usuario", usuario.buscar, methods=["GET"])
    app.add_url_rule("/usuarios", "criar_usuario", usuario.criar, methods=["POST"])
    app.add_url_rule("/login", "login", usuario.login, methods=["POST"])

    # Pedidos
    app.add_url_rule("/pedidos", "criar_pedido", pedido.criar, methods=["POST"])
    app.add_url_rule("/pedidos", "listar_todos_pedidos", pedido.listar_todos, methods=["GET"])
    app.add_url_rule(
        "/pedidos/usuario/<int:usuario_id>",
        "listar_pedidos_usuario",
        pedido.listar_por_usuario,
        methods=["GET"],
    )
    app.add_url_rule(
        "/pedidos/<int:pedido_id>/status",
        "atualizar_status_pedido",
        pedido.atualizar_status,
        methods=["PUT"],
    )

    # Relatórios
    app.add_url_rule("/relatorios/vendas", "relatorio_vendas", pedido.relatorio_vendas, methods=["GET"])

    # Health / index
    app.add_url_rule("/health", "health_check", health.health, methods=["GET"])
    app.add_url_rule("/", "index", health.index, methods=["GET"])
