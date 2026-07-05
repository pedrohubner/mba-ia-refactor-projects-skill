// Composition root / entry point.
// Cria o app, lê a config, conecta o banco, instancia models → services →
// controllers (injeção de dependência), registra rotas e o error handler.
const express = require('express');

const config = require('./config/settings');
const logger = require('./middlewares/logger');
const { createAndInit } = require('./database/connection');
const { errorHandler } = require('./middlewares/errorHandler');
const { buildRouter } = require('./views/routes');

const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const PaymentModel = require('./models/paymentModel');
const AuditModel = require('./models/auditModel');

const PaymentService = require('./services/paymentService');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const UserService = require('./services/userService');

const CheckoutController = require('./controllers/checkoutController');
const ReportController = require('./controllers/reportController');
const UserController = require('./controllers/userController');

async function createApp() {
    const conn = await createAndInit(config.dbPath);

    // Models
    const userModel = new UserModel(conn);
    const courseModel = new CourseModel(conn);
    const enrollmentModel = new EnrollmentModel(conn);
    const paymentModel = new PaymentModel(conn);
    const auditModel = new AuditModel(conn);

    // Services
    const paymentService = new PaymentService(config.paymentGatewayKey);
    const checkoutService = new CheckoutService({
        userModel, courseModel, enrollmentModel, paymentModel, auditModel, paymentService,
    });
    const reportService = new ReportService({ courseModel, enrollmentModel, userModel, paymentModel });
    const userService = new UserService({ userModel, enrollmentModel, paymentModel });

    // Controllers
    const controllers = {
        checkout: new CheckoutController(checkoutService),
        report: new ReportController(reportService),
        user: new UserController(userService),
    };

    const app = express();
    app.use(express.json());
    app.use(buildRouter(controllers));
    app.use(errorHandler);
    return app;
}

if (require.main === module) {
    createApp()
        .then((app) => {
            app.listen(config.port, () => {
                logger.info(`LMS API rodando na porta ${config.port}...`);
            });
        })
        .catch((err) => {
            logger.error(`Falha ao iniciar: ${err && err.message}`);
            process.exit(1);
        });
}

module.exports = { createApp };
