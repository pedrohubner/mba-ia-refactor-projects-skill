// Conexão + schema/seed + helpers promisificados.
// Substitui os callbacks aninhados do driver sqlite3 (finding H4 / API deprecada)
// por uma API async/await (playbook P8/P10).
const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

function createDatabase(dbPath) {
    const db = new sqlite3.Database(dbPath);

    // `db.run` usa `this.lastID`, então não pode ser um arrow promisify simples:
    const run = (sql, params = []) =>
        new Promise((resolve, reject) => {
            db.run(sql, params, function (err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    const get = promisify(db.get.bind(db));
    const all = promisify(db.all.bind(db));

    return { db, run, get, all };
}

async function initSchema(conn) {
    const { run } = conn;
    await run('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await run('CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await run('CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await run('CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await run('CREATE TABLE IF NOT EXISTS audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');
}

async function seedIfEmpty(conn) {
    const { get, run } = conn;
    const row = await get('SELECT COUNT(*) AS c FROM users');
    if (row && row.c > 0) return;

    const { hashPassword } = require('../services/passwordService');
    await run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan',
        'leonan@fullcycle.com.br',
        hashPassword('123'),
    ]);
    await run('INSERT INTO courses (title, price, active) VALUES (?, ?, 1), (?, ?, 1)', [
        'Clean Architecture', 997.0, 'Docker', 497.0,
    ]);
    await run('INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await run('INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, ?)', ['PAID']);
}

async function createAndInit(dbPath) {
    const conn = createDatabase(dbPath);
    await initSchema(conn);
    await seedIfEmpty(conn);
    return conn;
}

module.exports = { createAndInit };
