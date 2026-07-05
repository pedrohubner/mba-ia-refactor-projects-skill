// Regra de negócio do checkout (finding H1 — tirada da rota) escrita com
// async/await, eliminando a pirâmide de callbacks (finding H4 / playbook P10).
const { HttpError } = require('../middlewares/errorHandler');
const { hashPassword } = require('./passwordService');

class CheckoutService {
    constructor({ userModel, courseModel, enrollmentModel, paymentModel, auditModel, paymentService }) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditModel = auditModel;
        this.paymentService = paymentService;
    }

    async checkout({ name, email, password, courseId, card }) {
        if (!name || !email || !courseId || !card) {
            throw new HttpError(400, 'Bad Request');
        }

        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new HttpError(404, 'Curso não encontrado');

        // Cria o usuário se ainda não existir (senha com hash seguro).
        let user = await this.userModel.findByEmail(email);
        const userId = user
            ? user.id
            : await this.userModel.create(name, email, hashPassword(password || '123456'));

        const status = this.paymentService.charge(card, course.price);
        if (status === 'DENIED') throw new HttpError(400, 'Pagamento recusado');

        const enrollmentId = await this.enrollmentModel.create(userId, courseId);
        await this.paymentModel.create(enrollmentId, course.price, status);
        await this.auditModel.log(`Checkout curso ${courseId} por ${userId}`);

        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    }
}

module.exports = CheckoutService;
