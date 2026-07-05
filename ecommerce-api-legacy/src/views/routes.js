const express = require('express');

function buildRouter(controllers) {
    const router = express.Router();
    const { checkout, report, user } = controllers;

    router.post('/api/checkout', (req, res, next) => checkout.checkout(req, res, next));
    router.get('/api/admin/financial-report', (req, res, next) => report.financialReport(req, res, next));
    router.delete('/api/users/:id', (req, res, next) => user.remove(req, res, next));

    return router;
}

module.exports = { buildRouter };
