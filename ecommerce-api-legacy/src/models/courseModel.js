// Model de curso.
class CourseModel {
    constructor(conn) {
        this.conn = conn;
    }

    findActiveById(id) {
        return this.conn.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    }

    findAll() {
        return this.conn.all('SELECT * FROM courses', []);
    }
}

module.exports = CourseModel;
