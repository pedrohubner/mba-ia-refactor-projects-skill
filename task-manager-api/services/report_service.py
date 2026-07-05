"""Relatórios (findings H1/M1).

O relatório de resumo original fazia uma query de tasks por usuário dentro de um
loop (N+1). Aqui as tasks são carregadas uma única vez e agregadas em memória
(playbook P7). Datas via `now_utc()` (sem `utcnow()` deprecated).
"""
from datetime import timedelta

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import DomainError
from utils.helpers import now_utc, is_overdue


def summary_report():
    tasks = db.session.execute(db.select(Task)).scalars().all()
    users = db.session.execute(db.select(User)).scalars().all()
    total_categories = db.session.execute(
        db.select(db.func.count(Category.id))
    ).scalar()

    by_status = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    by_priority = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    seven_days_ago = now_utc() - timedelta(days=7)
    recent_created = 0
    recent_done = 0
    per_user = {u.id: {'user_id': u.id, 'user_name': u.name, 'total_tasks': 0, 'completed_tasks': 0} for u in users}

    for t in tasks:
        by_status[t.status] = by_status.get(t.status, 0) + 1
        by_priority[t.priority] = by_priority.get(t.priority, 0) + 1
        if is_overdue(t):
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (now_utc() - t.due_date).days,
            })
        if t.created_at and t.created_at >= seven_days_ago:
            recent_created += 1
        if t.status == 'done' and t.updated_at and t.updated_at >= seven_days_ago:
            recent_done += 1
        if t.user_id in per_user:
            per_user[t.user_id]['total_tasks'] += 1
            if t.status == 'done':
                per_user[t.user_id]['completed_tasks'] += 1

    user_stats = []
    for s in per_user.values():
        total = s['total_tasks']
        s['completion_rate'] = round((s['completed_tasks'] / total) * 100, 2) if total > 0 else 0
        user_stats.append(s)

    return {
        'generated_at': str(now_utc()),
        'overview': {
            'total_tasks': len(tasks),
            'total_users': len(users),
            'total_categories': total_categories,
        },
        'tasks_by_status': by_status,
        'tasks_by_priority': {
            'critical': by_priority.get(1, 0),
            'high': by_priority.get(2, 0),
            'medium': by_priority.get(3, 0),
            'low': by_priority.get(4, 0),
            'minimal': by_priority.get(5, 0),
        },
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_created,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise DomainError('Usuário não encontrado', 404)

    tasks = user.tasks
    counts = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    for t in tasks:
        counts[t.status] = counts.get(t.status, 0) + 1
        if t.priority <= 2:
            high_priority += 1
        if is_overdue(t):
            overdue += 1
    total = len(tasks)
    done = counts.get('done', 0)
    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': counts.get('pending', 0),
            'in_progress': counts.get('in_progress', 0),
            'cancelled': counts.get('cancelled', 0),
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        },
    }
