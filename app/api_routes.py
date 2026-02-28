from flask import Blueprint, request, jsonify
from app.models import Task, Subtask
from . import db

api = Blueprint('api', __name__)

@api.route('/api/ping')
def ping():
    return jsonify({'message': 'pong'})


@api.route('/api/tasks', methods=['GET'])
def get_active_tasks():
    tasks = Task.query.filter_by(completed=False, deleted=False).all()  # ✅ Only ongoing tasks
    result = []
    for task in tasks:
        subtasks = [{'id': st.id, 'title': st.title, 'completed': st.completed} for st in task.subtasks]
        result.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'subtasks': subtasks
        })
    return jsonify(result)


@api.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    subtasks = [{'id': st.id, 'title': st.title, 'completed': st.completed} for st in task.subtasks]
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
        'subtasks': subtasks
    })

@api.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    new_task = Task(title=title, description=description, completed=False)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created', 'task_id': new_task.id}), 201

@api.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
def add_subtask(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Subtask title is required'}), 400

    subtask = Subtask(title=title, task=task)
    db.session.add(subtask)
    db.session.commit()

    return jsonify({'message': 'Subtask added', 'subtask_id': subtask.id}), 201

@api.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200

@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated'}), 200

@api.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
def delete_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    db.session.delete(subtask)
    db.session.commit()
    return jsonify({'message': 'Subtask deleted'}), 200

@api.route('/api/tasks/<int:task_id>/description', methods=['PATCH'])
def update_description(task_id):
    data = request.get_json()
    new_description = data.get('description', '').strip()

    task = Task.query.get_or_404(task_id)
    task.description = new_description
    db.session.commit()

    return jsonify({"message": "Description updated"}), 200

@api.route('/mark_completed', methods=['POST'])
def mark_completed():
    data = request.get_json()
    completed_ids = data.get('completed_ids', [])

    for subtask_id in completed_ids:
        subtask = Subtask.query.get(int(subtask_id))
        if subtask:
            subtask.completed = True

    db.session.commit()
    return jsonify({"success": True})



