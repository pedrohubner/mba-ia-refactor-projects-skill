class AuditModel {
    constructor(conn) {
        this.conn = conn;
    }

    log(action) {
        return this.conn.run(
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action],
        );
    }
}

module.exports = AuditModel;
