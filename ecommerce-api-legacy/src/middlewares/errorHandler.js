// Tratamento de erro centralizado (finding M4 / playbook P5).
// Substitui os erros engolidos e os `res.status(500)` repetidos em cada callback.
const logger = require('./logger');

class HttpError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

function errorHandler(err, req, res, next) {
    if (err instanceof HttpError) {
        return res.status(err.status).json({ error: err.message });
    }
    logger.error(`Erro inesperado: ${err && err.message}`);
    return res.status(500).json({ error: 'Erro interno' });
}

module.exports = { HttpError, errorHandler };
