"""Regra de negócio de usuários (findings H1/M2)."""
from database import db
from models.user import User
from models.task import Task
from middlewares.error_handler import DomainError
from utils.helpers import validate_email
from config.settings import VALID_ROLES, PASSWORD_MIN


def list_users():
    users = db.session.execute(db.select(User)).scalars().all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise DomainError('Usuário não encontrado', 404)
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in user.tasks]
    return data


def create_user(data):
    if not data:
        raise DomainError('Dados inválidos', 400)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise DomainError('Nome é obrigatório', 400)
    if not email:
        raise DomainError('Email é obrigatório', 400)
    if not password:
        raise DomainError('Senha é obrigatória', 400)
    if not validate_email(email):
        raise DomainError('Email inválido', 400)
    if len(password) < PASSWORD_MIN:
        raise DomainError(f'Senha deve ter no mínimo {PASSWORD_MIN} caracteres', 400)
    if role not in VALID_ROLES:
        raise DomainError('Role inválido', 400)
    if db.session.execute(db.select(User).where(User.email == email)).scalar_one_or_none():
        raise DomainError('Email já cadastrado', 409)

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role
    db.session.add(user)
    db.session.commit()
    return user.to_dict()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        raise DomainError('Usuário não encontrado', 404)
    if not data:
        raise DomainError('Dados inválidos', 400)

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        if not validate_email(data['email']):
            raise DomainError('Email inválido', 400)
        existing = db.session.execute(
            db.select(User).where(User.email == data['email'])
        ).scalar_one_or_none()
        if existing and existing.id != user_id:
            raise DomainError('Email já cadastrado', 409)
        user.email = data['email']
    if 'password' in data:
        if len(data['password']) < PASSWORD_MIN:
            raise DomainError('Senha muito curta', 400)
        user.set_password(data['password'])
    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise DomainError('Role inválido', 400)
        user.role = data['role']
    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise DomainError('Usuário não encontrado', 404)
    for t in list(user.tasks):
        db.session.delete(t)
    db.session.delete(user)
    db.session.commit()


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise DomainError('Usuário não encontrado', 404)
    from services.task_service import serialize
    return [serialize(t) for t in user.tasks]


def login(data):
    if not data:
        raise DomainError('Dados inválidos', 400)
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise DomainError('Email e senha são obrigatórios', 400)
    user = db.session.execute(
        db.select(User).where(User.email == email)
    ).scalar_one_or_none()
    if not user or not user.check_password(password):
        raise DomainError('Credenciais inválidas', 401)
    if not user.active:
        raise DomainError('Usuário inativo', 403)
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }
