"""Helpers puros e reutilizáveis.

- `now_utc()` substitui `datetime.utcnow()` (API deprecated no Python 3.12+) por
  `datetime.now(timezone.utc)`, mantendo o valor *naive* para permanecer
  compatível com as colunas naive já persistidas.
- `is_overdue()` centraliza a lógica de atraso que estava duplicada em várias
  rotas (findings M3/DRY).
- Imports não usados do arquivo original foram removidos (finding L4).
"""
import re
from datetime import datetime, timezone


def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_overdue(task):
    """Uma task está atrasada se venceu e não está concluída/cancelada."""
    return bool(
        task.due_date
        and task.due_date < now_utc()
        and task.status not in ("done", "cancelled")
    )


def validate_email(email):
    return bool(re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", email))


def calculate_percentage(part, total):
    if not total:
        return 0
    return round((part / total) * 100, 2)


def parse_date(date_string):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    return None
