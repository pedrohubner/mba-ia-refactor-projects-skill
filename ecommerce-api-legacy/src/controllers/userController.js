// Controller de usuário.
class UserController {
    constructor(userService) {
        this.userService = userService;
    }

    async remove(req, res, next) {
        try {
            await this.userService.deleteUser(req.params.id);
            res.json({ msg: 'Usuário e dados relacionados removidos com sucesso' });
        } catch (err) {
            next(err);
        }
    }
}

module.exports = UserController;
