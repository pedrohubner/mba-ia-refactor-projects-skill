class UserService {
    constructor({ userModel, enrollmentModel, paymentModel }) {
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
    }

    async deleteUser(userId) {
        await this.paymentModel.deleteByUser(userId);
        await this.enrollmentModel.deleteByUser(userId);
        await this.userModel.delete(userId);
    }
}

module.exports = UserService;
