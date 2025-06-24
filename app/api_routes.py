from flask import Blueprint, request, jsonify
from app.models import Task, Subtask
from . import db

api = Blueprint('api', __name__)

@api.route('/api/ping')
def ping():
    return jsonify({'message': 'pong'})


@api.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
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

from flask import Blueprint, request, jsonify
from app.models import Category, CategoryItem
from . import db

api = Blueprint('api', __name__)


@api.route('/api/ping')
def ping():
    return jsonify({'message': 'pong'})



@api.route('/api/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for category in categories:
        items = [{'id': item.id, 'title': item.title, 'selected': item.selected} for item in category.items]
        result.append({
            'id': category.id,
            'name': category.name,
            'items': items
        })
    return jsonify(result)


@api.route('/api/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    items = [{'id': item.id, 'title': item.title, 'selected': item.selected} for item in category.items]
    return jsonify({
        'id': category.id,
        'name': category.name,
        'items': items
    })


@api.route('/api/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    new_category = Category(name=name)
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'message': 'Category created', 'category_id': new_category.id}), 201


@api.route('/api/categories/<int:category_id>/items', methods=['POST'])
def create_category_item(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    title = data.get('title')

    if not title:
        return jsonify({'error': 'Item title is required'}), 400

    item = CategoryItem(title=title, category=category)
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': 'Item added', 'item_id': item.id}), 201


@api.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    category.name = data.get('name', category.name)
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


from flask import Blueprint, request, jsonify
from app.models import Profile
from app import db

profile_api = Blueprint('profile_api', __name__)




@api.route('/api/profiles/<int:id>', methods=['GET'])
def get_profile(id):
    profile = Profile.query.get_or_404(id)
    return jsonify({
        'id': profile.id,
        'username': profile.username,
        'first_name': profile.first_name,
        'last_name': profile.last_name,
        'email': profile.email,
        'image_filename': profile.image_filename
    })


@api.route('/api/profiles/<int:id>', methods=['PUT'])
def update_profile(id):
    profile = Profile.query.get_or_404(id)
    data = request.get_json()

    profile.username = data.get('username', profile.username)
    profile.first_name = data.get('first_name', profile.first_name)
    profile.last_name = data.get('last_name', profile.last_name)
    profile.email = data.get('email', profile.email)
    profile.image_filename = data.get('image_filename', profile.image_filename)

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'}), 200

@api.route('/api/profiles', methods=['POST'])
def create_profile():
    data = request.get_json()
    if not data.get('username') or not data.get('email'):
        return jsonify({'error': 'Username and Email are required'}), 400

    profile = Profile(
        username=data['username'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        email=data['email'],
        image_filename=data.get('image_filename', 'images/profile.png')
    )
    db.session.add(profile)
    db.session.commit()
    return jsonify({'message': 'Profile created', 'id': profile.id}), 201
