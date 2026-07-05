"""Regra de negócio de tasks (findings H1/M1/M2/M3).

- Serialização centralizada (fim da duplicação do bloco `overdue`).
- Listagem com eager loading (joinedload) elimina o N+1 que fazia uma query de
  usuário e outra de categoria por task (playbook P7).
- `db.session.get(...)` no lugar de `Model.query.get(...)` deprecated (P8).
"""
from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import DomainError
from utils.helpers import now_utc, is_overdue, parse_date
from config.settings import VALID_STATUSES, PRIORITY_MIN, PRIORITY_MAX, TITLE_MIN, TITLE_MAX


def serialize(task, with_relations=False):
    data = task.to_dict()
    data['overdue'] = is_overdue(task)
    if with_relations:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = db.session.execute(
        db.select(Task).options(joinedload(Task.user), joinedload(Task.category))
    ).scalars().all()
    return [serialize(t, with_relations=True) for t in tasks]


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise DomainError('Task não encontrada', 404)
    return serialize(task)


def _validate_title(title):
    if not title:
        raise DomainError('Título é obrigatório', 400)
    if len(title) < TITLE_MIN:
        raise DomainError('Título muito curto', 400)
    if len(title) > TITLE_MAX:
        raise DomainError('Título muito longo', 400)


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise DomainError('Status inválido', 400)


def _validate_priority(priority):
    if priority < PRIORITY_MIN or priority > PRIORITY_MAX:
        raise DomainError(f'Prioridade deve ser entre {PRIORITY_MIN} e {PRIORITY_MAX}', 400)


def _check_fk(user_id, category_id):
    if user_id and not db.session.get(User, user_id):
        raise DomainError('Usuário não encontrado', 404)
    if category_id and not db.session.get(Category, category_id):
        raise DomainError('Categoria não encontrada', 404)


def _apply_tags(task, tags):
    task.tags = ','.join(tags) if isinstance(tags, list) else tags


def create_task(data):
    if not data:
        raise DomainError('Dados inválidos', 400)
    title = data.get('title')
    _validate_title(title)
    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    _validate_status(status)
    _validate_priority(priority)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    _check_fk(user_id, category_id)

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id
    if data.get('due_date'):
        parsed = parse_date(data['due_date'])
        if not parsed:
            raise DomainError('Formato de data inválido. Use YYYY-MM-DD', 400)
        task.due_date = parsed
    if data.get('tags'):
        _apply_tags(task, data['tags'])

    db.session.add(task)
    db.session.commit()
    return serialize(task)


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        raise DomainError('Task não encontrada', 404)
    if not data:
        raise DomainError('Dados inválidos', 400)

    if 'title' in data:
        _validate_title(data['title'])
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        _validate_status(data['status'])
        task.status = data['status']
    if 'priority' in data:
        _validate_priority(data['priority'])
        task.priority = data['priority']
    if 'user_id' in data:
        _check_fk(data['user_id'], None)
        task.user_id = data['user_id']
    if 'category_id' in data:
        _check_fk(None, data['category_id'])
        task.category_id = data['category_id']
    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date'])
            if not parsed:
                raise DomainError('Formato de data inválido', 400)
            task.due_date = parsed
        else:
            task.due_date = None
    if 'tags' in data:
        _apply_tags(task, data['tags'])

    task.updated_at = now_utc()
    db.session.commit()
    return serialize(task)


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise DomainError('Task não encontrada', 404)
    db.session.delete(task)
    db.session.commit()


def search_tasks(query='', status='', priority='', user_id=''):
    stmt = db.select(Task)
    if query:
        stmt = stmt.where(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        stmt = stmt.where(Task.status == status)
    if priority:
        stmt = stmt.where(Task.priority == int(priority))
    if user_id:
        stmt = stmt.where(Task.user_id == int(user_id))
    tasks = db.session.execute(stmt).scalars().all()
    return [t.to_dict() for t in tasks]


def task_stats():
    tasks = db.session.execute(db.select(Task)).scalars().all()
    total = len(tasks)
    counts = {s: 0 for s in VALID_STATUSES}
    overdue = 0
    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
        if is_overdue(t):
            overdue += 1
    done = counts.get('done', 0)
    return {
        'total': total,
        'pending': counts.get('pending', 0),
        'in_progress': counts.get('in_progress', 0),
        'done': done,
        'cancelled': counts.get('cancelled', 0),
        'overdue': overdue,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
