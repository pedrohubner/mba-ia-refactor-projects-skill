// Controller do relatório financeiro.
class ReportController {
    constructor(reportService) {
        this.reportService = reportService;
    }

    async financialReport(req, res, next) {
        try {
            const report = await this.reportService.financialReport();
            res.json(report);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = ReportController;
