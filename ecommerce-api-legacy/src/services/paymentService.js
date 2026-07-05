const logger = require('../middlewares/logger');

class PaymentService {
    constructor(gatewayKey) {
        this.gatewayKey = gatewayKey;
    }

    charge(cardNumber, amount) {
        logger.info(`Processando pagamento de ${amount} (cartão ****${String(cardNumber).slice(-4)})`);
        const approved = String(cardNumber).startsWith('4');
        return approved ? 'PAID' : 'DENIED';
    }
}

module.exports = PaymentService;
