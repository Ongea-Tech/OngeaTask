from flask import Blueprint, request, jsonify
from app.models import Task, Subtask, Category
from . import db
from flask_login import login_required, current_user

api = Blueprint('api', __name__)

@api.route('/api/tasks', methods=['GET'])
@login_required
def get_active_tasks():
    """Gets all the ongoing incomplete tasks"""
    tasks = Task.query.filter_by(user_id = current_user.id, completed=False, deleted=False).all()  # ✅ Only ongoing tasks
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
@login_required
def get_task(task_id):
    """Gets a specific task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    subtasks = [{'id': st.id, 'title': st.title, 'completed': st.completed} for st in task.subtasks]
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'completed': task.completed,
        'subtasks': subtasks
    })



    
@api.route('/api/tasks', methods=['POST'])
@login_required
@login_required
def create_task():
    """Creates a new task"""
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    
    if not title:
        return jsonify({'error': 'Title is required'}), 400

    new_task = Task(title=title, description=description, completed=False, user_id = current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task created', 'task_id': new_task.id}), 201


@api.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
@login_required
@login_required
def add_subtask(task_id):
    """Adds a new subtask to a specific task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Subtask title is required'}), 400

    subtask = Subtask(title=title, task=task)
    db.session.add(subtask)
    db.session.commit()

    return jsonify({'message': 'Subtask added', 'subtask_id': subtask.id}), 201


@api.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
@login_required
def delete_task(task_id):
    """Deletes a specific task"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200


@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
@login_required
def update_task(task_id):
    """Updates old records of a specific task with data provided by the user"""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    db.session.commit()
    return jsonify({'message': 'Task updated'}), 200


@api.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
@login_required
@login_required
def delete_subtask(subtask_id):
    """Deletes a subtask from the database"""
    subtask = Subtask.query.join(Task).filter(Subtask.id == subtask_id, Task.user_id == current_user.id).first_or_404()
    db.session.delete(subtask)
    db.session.commit()
    return jsonify({'message': 'Subtask deleted'}), 200


@api.route('/api/tasks/<int:task_id>/description', methods=['PATCH'])
@login_required
@login_required
def update_description(task_id):
    """Updates the old description with new description provided by the user"""
    data = request.get_json()
    new_description = data.get('description', '').strip()

    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.description = new_description
    db.session.commit()

    return jsonify({"message": "Description updated"}), 200


@api.route('/mark_completed', methods=['POST'])
@login_required
@login_required
def mark_completed():
    """Marks subtasks as completed"""
    data = request.get_json()
    completed_ids = data.get('completed_ids', [])

    for subtask_id in completed_ids:
        subtask = Subtask.query.join(Task).filter(
            Subtask.id == int(subtask_id),
            Task.user_id == current_user.id
        ).first()
        if subtask:
            subtask.completed = True

    db.session.commit()
    return jsonify({"success": True})
#Category Endpoints
@api.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    """Gets all categories for the current user"""
    categories = Category.query.all()
    result = []
    for cat in categories:
        result.append({
            'id': cat.id,
            'name': cat.name,
            'color': cat.color
        })
    return jsonify(result)


@api.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    """Creates a new category"""
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    # Frontend may send a color, fallback to blue if missing
    color = data.get('color', '#3b82f6')

    new_category = Category(name=name, color=color)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({
        'message': 'Category created',
        'category_id': new_category.id,
        'name': new_category.name,
        'color': new_category.color
    }), 201
@api.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """Updates a specific category (name & color)"""
    category = Category.query.filter_by(id=category_id).first_or_404()
    data = request.get_json()
    
    # Only update fields if they were sent
    if 'name' in data:
        category.name = data['name']
    if 'color' in data:
        category.color = data['color']
        
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated',
        'id': category.id,
        'name': category.name,
        'color': category.color
    }), 200
@api.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Deletes a specific category"""
    category = Category.query.filter_by(id=category_id).first_or_404()
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted'}), 200
@api.route('/api/categories/delete-multiple', methods=['POST'])
@login_required
def delete_multiple_categories():
    """Deletes multiple categories at once"""
    data = request.get_json()
    category_ids = data.get('ids', [])

    if not category_ids or not isinstance(category_ids, list):
        return jsonify({'error': 'List of category IDs is required'}), 400

    # Convert string IDs (from dataset.id) to integers for SQLAlchemy
    category_ids = [int(i) for i in category_ids]

    # Fetch categories that actually exist in the DB
    categories = Category.query.filter(Category.id.in_(category_ids)).all()
    deleted_ids = [cat.id for cat in categories]

    # Delete them in one transaction
    for cat in categories:
        db.session.delete(cat)
    db.session.commit()

    # ✅ Return exactly what the frontend checks: `deleted_ids`
    return jsonify({
        'deleted_ids': deleted_ids,
        'message': f'{len(deleted_ids)} categories deleted successfully'
    }), 200