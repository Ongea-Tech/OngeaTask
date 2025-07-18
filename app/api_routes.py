from flask import Blueprint, request, jsonify
from app.models import Task, Subtask, Category, Profile
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

@api.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        result.append({
            'id': category.id,
            'name': category.name,
            'color': category.color
        })
    return jsonify(result)


@api.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({
        'id': category.id,
        'name': category.name,
        'color': category.color
    })


@api.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')
    color = data.get('color', '#cccccc')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    new_category = Category(name=name, color=color)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category_id': new_category.id}), 201


@api.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data.get('name', category.name)
    category.color = data.get('color', category.color)
    db.session.commit()
    return jsonify({'message': 'Category updated'}), 200


@api.route('/api/categories/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200


@api.route('/api/categories/delete-multiple', methods=['POST'])
def delete_multiple_categories():
    data = request.get_json()
    ids = data.get('ids')

    if not ids or not isinstance(ids, list):
        return jsonify({'error': 'A list of category IDs is required'}), 400

    categories = Category.query.filter(Category.id.in_(ids)).all()

    if not categories:
        return jsonify({'error': 'No matching categories found'}), 404

    try:
        for category in categories:
            db.session.delete(category)
        db.session.commit()
        return jsonify({'message': 'Categories deleted', 'deleted_ids': ids}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


import os
from werkzeug.utils import secure_filename
from flask import current_app


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@api.route('/api/profiles/<int:id>', methods=['PUT'])
def update_profile(id):
    profile = Profile.query.get_or_404(id)
    username = request.form.get('username', profile.username)
    first_name = request.form.get('first_name', profile.first_name)
    last_name = request.form.get('last_name', profile.last_name)
    email = request.form.get('email', profile.email)

    profile.username = username
    profile.first_name = first_name
    profile.last_name = last_name
    profile.email = email

    
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

          
            profile.image_filename = f'uploads/{filename}'

    
    db.session.commit()

    return jsonify({
        'message': 'Profile updated successfully',
        'image_filename': profile.image_filename
    }), 200
