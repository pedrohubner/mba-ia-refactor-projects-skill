from database import db
from utils.helpers import now_utc
import hashlib
import os

_PBKDF2_ROUNDS = 120_000


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now_utc)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, _PBKDF2_ROUNDS)
        self.password = f'pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}'

    def check_password(self, pwd):
        try:
            algo, rounds, salt_hex, hash_hex = self.password.split('$')
            if algo != 'pbkdf2_sha256':
                return False
            salt = bytes.fromhex(salt_hex)
            calc = hashlib.pbkdf2_hmac('sha256', pwd.encode(), salt, int(rounds))
            return calc.hex() == hash_hex
        except (ValueError, AttributeError):
            return False

    def is_admin(self):
        return self.role == 'admin'
