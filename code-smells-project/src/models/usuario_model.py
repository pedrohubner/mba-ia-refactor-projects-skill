import hashlib
import os

_PBKDF2_ROUNDS = 120_000


def hash_senha(senha):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, _PBKDF2_ROUNDS)
    return f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt.hex()}${digest.hex()}"


def verificar_senha(senha, armazenada):
    try:
        algo, rounds, salt_hex, hash_hex = armazenada.split("$")
        if algo != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        calc = hashlib.pbkdf2_hmac("sha256", senha.encode(), salt, int(rounds))
        return calc.hex() == hash_hex
    except (ValueError, AttributeError):
        return False


def _to_public_dict(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


class UsuarioModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios")
        return [_to_public_dict(r) for r in cur.fetchall()]

    def get_by_id(self, usuario_id):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        row = cur.fetchone()
        return _to_public_dict(row) if row else None

    def create(self, nome, email, senha, tipo="cliente"):
        cur = self.db.cursor()
        cur.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, hash_senha(senha), tipo),
        )
        self.db.commit()
        return cur.lastrowid

    def authenticate(self, email, senha):
        cur = self.db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cur.fetchone()
        if row and verificar_senha(senha, row["senha"]):
            return _to_public_dict(row)
        return None
