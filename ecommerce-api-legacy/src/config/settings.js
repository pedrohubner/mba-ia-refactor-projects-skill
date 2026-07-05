module.exports = {
    port: Number(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || ':memory:',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'test-key',
    smtpUser: process.env.SMTP_USER || 'no-reply@example.com',
};
