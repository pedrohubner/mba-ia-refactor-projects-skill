"""Controller de tasks — traduz HTTP ↔ service. Sem regra de negócio nem SQL."""
from flask import request, jsonify

from services import task_service


def get_tasks():
    return jsonify(task_service.list_tasks()), 200


def get_task(task_id):
    return jsonify(task_service.get_task(task_id)), 200


def create_task():
    task = task_service.create_task(request.get_json())
    return jsonify(task), 201


def update_task(task_id):
    task = task_service.update_task(task_id, request.get_json())
    return jsonify(task), 200


def delete_task(task_id):
    task_service.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200


def search_tasks():
    result = task_service.search_tasks(
        query=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify(result), 200


def task_stats():
    return jsonify(task_service.task_stats()), 200
