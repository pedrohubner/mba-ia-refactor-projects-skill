class EnrollmentModel {
    constructor(conn) {
        this.conn = conn;
    }

    async create(userId, courseId) {
        const { lastID } = await this.conn.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId],
        );
        return lastID;
    }

    findByCourse(courseId) {
        return this.conn.all('SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
    }

    findAll() {
        return this.conn.all('SELECT * FROM enrollments', []);
    }

    deleteByUser(userId) {
        return this.conn.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    }
}

module.exports = EnrollmentModel;
