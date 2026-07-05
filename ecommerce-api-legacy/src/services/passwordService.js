const crypto = require('crypto');

function hashPassword(plain) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(plain), salt, 32).toString('hex');
    return `scrypt$${salt}$${derived}`;
}

function verifyPassword(plain, stored) {
    try {
        const [algo, salt, hash] = stored.split('$');
        if (algo !== 'scrypt') return false;
        const derived = crypto.scryptSync(String(plain), salt, 32).toString('hex');
        return crypto.timingSafeEqual(Buffer.from(hash, 'hex'), Buffer.from(derived, 'hex'));
    } catch (e) {
        return false;
    }
}

module.exports = { hashPassword, verifyPassword };
