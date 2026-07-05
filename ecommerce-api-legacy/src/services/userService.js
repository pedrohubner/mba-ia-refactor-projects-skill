// Regra de deleção de usuário com integridade referencial (finding M5).
// O original deletava só o usuário e deixava matrículas e pagamentos órfãos.
class UserService {
    constructor({ userModel, enrollmentModel, paymentModel }) {
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
    }

    async deleteUser(userId) {
        // Ordem importa: pagamentos → matrículas → usuário.
        await this.paymentModel.deleteByUser(userId);
        await this.enrollmentModel.deleteByUser(userId);
        await this.userModel.delete(userId);
    }
}

module.exports = UserService;
