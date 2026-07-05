// Simulação de gateway de pagamento isolada em um service.
// NÃO loga o número do cartão nem a chave do gateway (finding C1 — dado sensível
// era impresso no console no código original).
const logger = require('../middlewares/logger');

class PaymentService {
    constructor(gatewayKey) {
        this.gatewayKey = gatewayKey;
    }

    // Regra simulada preservada: cartões que começam com "4" são aprovados.
    charge(cardNumber, amount) {
        logger.info(`Processando pagamento de ${amount} (cartão ****${String(cardNumber).slice(-4)})`);
        const approved = String(cardNumber).startsWith('4');
        return approved ? 'PAID' : 'DENIED';
    }
}

module.exports = PaymentService;
