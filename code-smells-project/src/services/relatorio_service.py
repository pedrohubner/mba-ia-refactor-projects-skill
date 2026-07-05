"""Regra de negócio do relatório de vendas (finding H1/L1).

A lógica de faixas de desconto sai do model/controller e vira regra explícita,
sem magic numbers soltos.
"""

# Faixas de desconto: (faturamento_minimo, taxa) — elimina magic numbers (L1).
DESCONTO_FAIXAS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]


def calcular_desconto(faturamento):
    for limite, taxa in DESCONTO_FAIXAS:
        if faturamento > limite:
            return round(faturamento * taxa, 2)
    return 0.0


class RelatorioService:
    def __init__(self, pedido_model):
        self.pedido_model = pedido_model

    def gerar_relatorio_vendas(self):
        total_pedidos = self.pedido_model.contar_todos()
        faturamento = self.pedido_model.faturamento_total()
        desconto = calcular_desconto(faturamento)
        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, 2),
            "desconto_aplicavel": desconto,
            "faturamento_liquido": round(faturamento - desconto, 2),
            "pedidos_pendentes": self.pedido_model.contar_por_status("pendente"),
            "pedidos_aprovados": self.pedido_model.contar_por_status("aprovado"),
            "pedidos_cancelados": self.pedido_model.contar_por_status("cancelado"),
            "ticket_medio": round(faturamento / total_pedidos, 2)
            if total_pedidos > 0
            else 0,
        }
