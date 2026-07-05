class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
    }

    async checkout(req, res, next) {
        try {
            const result = await this.checkoutService.checkout({
                name: req.body.usr,
                email: req.body.eml,
                password: req.body.pwd,
                courseId: req.body.c_id,
                card: req.body.card,
            });
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = CheckoutController;
