class PaymentModel {
    constructor(conn) {
        this.conn = conn;
    }

    create(enrollmentId, amount, status) {
        return this.conn.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status],
        );
    }

    findByEnrollment(enrollmentId) {
        return this.conn.get(
            'SELECT amount, status FROM payments WHERE enrollment_id = ?',
            [enrollmentId],
        );
    }

    findAll() {
        return this.conn.all('SELECT enrollment_id, amount, status FROM payments', []);
    }

    async deleteByUser(userId) {
        return this.conn.run(
            `DELETE FROM payments WHERE enrollment_id IN (
                SELECT id FROM enrollments WHERE user_id = ?
            )`,
            [userId],
        );
    }
}

module.exports = PaymentModel;
