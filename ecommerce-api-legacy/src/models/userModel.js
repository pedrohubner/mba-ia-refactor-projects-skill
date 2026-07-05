class UserModel {
    constructor(conn) {
        this.conn = conn;
    }

    findByEmail(email) {
        return this.conn.get('SELECT * FROM users WHERE email = ?', [email]);
    }

    async create(name, email, passHash) {
        const { lastID } = await this.conn.run(
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passHash],
        );
        return lastID;
    }

    delete(id) {
        return this.conn.run('DELETE FROM users WHERE id = ?', [id]);
    }

    findById(id) {
        return this.conn.get('SELECT id, name, email FROM users WHERE id = ?', [id]);
    }

    findAll() {
        return this.conn.all('SELECT id, name, email FROM users', []);
    }
}

module.exports = UserModel;
