"""API routes for OngeaTask — fully user-scoped, no duplicate decorators."""
import os
import json
import urllib.request
import urllib.parse
from datetime import date

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app.models import Task, Subtask, Category
from . import db

api = Blueprint('api', __name__)


# ─────────────────────────────────────────────
# HELPER: OpenAI call via urllib (no openai pkg needed)
# ─────────────────────────────────────────────
def openai_chat(prompt: str, system: str = "You are a helpful assistant.", max_tokens: int = 200) -> str:
    """Call OpenAI chat completions API using only stdlib urllib."""
    api_key = os.environ.get('OPENAI_API_KEY', '')
    if not api_key:
        return ''
    payload = json.dumps({
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": 0.4
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.openai.com/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return ''


# ─────────────────────────────────────────────
# TASK ENDPOINTS
# ─────────────────────────────────────────────

@api.route('/api/tasks', methods=['GET'])
@login_required
def get_active_tasks():
    """Gets all ongoing incomplete tasks for the current user."""
    tasks = Task.query.filter_by(
        user_id=current_user.id, completed=False, deleted=False
    ).all()
    return jsonify([t.to_dict() for t in tasks])


@api.route('/api/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """Gets a specific task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return jsonify(task.to_dict())


@api.route('/api/tasks', methods=['POST'])
@login_required
def create_task():
    """Creates a new task. Accepts optional category_ids list."""
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category_ids = data.get('category_ids', [])
    priority = data.get('priority', 'Medium')

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    new_task = Task(
        title=title,
        description=description or None,
        completed=False,
        user_id=current_user.id,
        priority=priority
    )

    # Link categories — only user's own categories
    if category_ids:
        cats = Category.query.filter(
            Category.id.in_(category_ids),
            Category.user_id == current_user.id
        ).all()
        new_task.categories.extend(cats)

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        'message': 'Task created',
        'task': new_task.to_dict()
    }), 201


@api.route('/api/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Updates a task. Accepts optional category_ids for re-assignment."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()

    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.completed = data.get('completed', task.completed)
    task.priority = data.get('priority', task.priority)

    if 'category_ids' in data:
        cats = Category.query.filter(
            Category.id.in_(data['category_ids']),
            Category.user_id == current_user.id
        ).all()
        task.categories = cats

    db.session.commit()
    return jsonify({'message': 'Task updated', 'task': task.to_dict()}), 200


@api.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    """Permanently deletes a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted'}), 200


@api.route('/api/tasks/<int:task_id>/description', methods=['PATCH'])
@login_required
def update_description(task_id):
    """Updates task description."""
    data = request.get_json()
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.description = data.get('description', '').strip()
    db.session.commit()
    return jsonify({'message': 'Description updated'}), 200


# ─────────────────────────────────────────────
# SUBTASK ENDPOINTS
# ─────────────────────────────────────────────

@api.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
@login_required
def add_subtask(task_id):
    """Adds a subtask to a task."""
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Subtask title is required'}), 400

    subtask = Subtask(title=title, task=task)
    db.session.add(subtask)
    db.session.commit()
    return jsonify({'message': 'Subtask added', 'subtask_id': subtask.id}), 201


@api.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
@login_required
def delete_subtask(subtask_id):
    """Deletes a subtask."""
    subtask = Subtask.query.join(Task).filter(
        Subtask.id == subtask_id,
        Task.user_id == current_user.id
    ).first_or_404()
    db.session.delete(subtask)
    db.session.commit()
    return jsonify({'message': 'Subtask deleted'}), 200


@api.route('/mark_completed', methods=['POST'])
@login_required
def mark_completed():
    """Marks subtasks as completed."""
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
    return jsonify({'success': True})


# ─────────────────────────────────────────────
# CATEGORY ENDPOINTS — User-Scoped
# ─────────────────────────────────────────────

@api.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    """Gets all non-archived categories for the current user, with stats."""
    include_archived = request.args.get('archived', 'false').lower() == 'true'
    query = Category.query.filter_by(user_id=current_user.id)
    if not include_archived:
        query = query.filter_by(archived=False)
    categories = query.order_by(Category.created_at.desc()).all()
    return jsonify([c.to_dict(include_stats=True) for c in categories])


@api.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    """Creates a new category for the current user."""
    data = request.get_json()
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Category name is required'}), 400

    # Check for duplicate name per user
    existing = Category.query.filter_by(user_id=current_user.id, name=name).first()
    if existing:
        return jsonify({'error': f'A category named "{name}" already exists'}), 409

    color = data.get('color', '#3b82f6')
    icon = data.get('icon', 'fa-folder')
    description = data.get('description', '').strip() or None

    new_cat = Category(
        user_id=current_user.id,
        name=name,
        color=color,
        icon=icon,
        description=description
    )
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({
        'message': 'Category created',
        'category': new_cat.to_dict(include_stats=True)
    }), 201


@api.route('/api/categories/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    """Gets a specific category with its tasks."""
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    data = category.to_dict(include_stats=True)
    # Include tasks in this category
    tasks = category.tasks.filter_by(deleted=False).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    return jsonify(data)


@api.route('/api/categories/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    """Updates a category (name, color, icon, description)."""
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    data = request.get_json()

    new_name = data.get('name', category.name).strip()
    if new_name != category.name:
        duplicate = Category.query.filter_by(
            user_id=current_user.id, name=new_name
        ).first()
        if duplicate:
            return jsonify({'error': f'Category "{new_name}" already exists'}), 409

    category.name = new_name
    if 'color' in data:
        category.color = data['color']
    if 'icon' in data:
        category.icon = data['icon']
    if 'description' in data:
        category.description = data['description'].strip() or None

    db.session.commit()
    return jsonify({
        'message': 'Category updated',
        'category': category.to_dict(include_stats=True)
    }), 200


@api.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    """Deletes a category. Tasks are unlinked, not deleted."""
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted'}), 200


@api.route('/api/categories/<int:category_id>/archive', methods=['PATCH'])
@login_required
def toggle_archive_category(category_id):
    """Toggles archived state of a category."""
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    category.archived = not category.archived
    db.session.commit()
    return jsonify({
        'message': 'Archived' if category.archived else 'Unarchived',
        'archived': category.archived
    }), 200


@api.route('/api/categories/delete-multiple', methods=['POST'])
@login_required
def delete_multiple_categories():
    """Deletes multiple categories at once."""
    data = request.get_json()
    category_ids = data.get('ids', [])
    if not category_ids or not isinstance(category_ids, list):
        return jsonify({'error': 'List of category IDs required'}), 400

    category_ids = [int(i) for i in category_ids]
    categories = Category.query.filter(
        Category.id.in_(category_ids),
        Category.user_id == current_user.id
    ).all()
    deleted_ids = [c.id for c in categories]
    for cat in categories:
        db.session.delete(cat)
    db.session.commit()
    return jsonify({
        'deleted_ids': deleted_ids,
        'message': f'{len(deleted_ids)} categories deleted'
    }), 200


@api.route('/api/categories/<int:category_id>/tasks', methods=['POST'])
@login_required
def add_task_to_category(category_id):
    """Creates a new task and adds it directly to a category."""
    category = Category.query.filter_by(
        id=category_id, user_id=current_user.id
    ).first_or_404()
    data = request.get_json()
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Task title is required'}), 400

    new_task = Task(
        title=title,
        description=data.get('description', '').strip() or None,
        completed=False,
        user_id=current_user.id,
        priority=data.get('priority', 'Medium')
    )
    new_task.categories.append(category)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({
        'message': 'Task added to category',
        'task': new_task.to_dict()
    }), 201


# ─────────────────────────────────────────────
# AI ENDPOINTS
# ─────────────────────────────────────────────

@api.route('/api/tasks/suggest-category', methods=['POST'])
@login_required
def suggest_category():
    """Uses OpenAI to suggest the best category for a task."""
    data = request.get_json()
    task_title = data.get('title', '').strip()
    task_desc = data.get('description', '').strip()

    if not task_title:
        return jsonify({'suggested_category': None}), 200

    categories = Category.query.filter_by(
        user_id=current_user.id, archived=False
    ).all()
    if not categories:
        return jsonify({'suggested_category': None}), 200

    cat_names = [c.name for c in categories]
    prompt = (
        f'Task title: "{task_title}"\n'
        f'Description: "{task_desc}"\n\n'
        f'Available categories: {", ".join(cat_names)}\n\n'
        f'Which single category best fits this task? '
        f'Reply with ONLY the exact category name from the list, or "None" if none fit.'
    )
    suggestion = openai_chat(prompt, system='You are a task organization assistant. Reply with only the category name.')

    # Validate the suggestion is actually one of the categories
    matched = next((c for c in categories if c.name.lower() == suggestion.lower()), None)
    return jsonify({
        'suggested_category': matched.name if matched else None,
        'suggested_category_id': matched.id if matched else None,
        'suggested_color': matched.color if matched else None
    })


@api.route('/api/categories/smart-create', methods=['POST'])
@login_required
def smart_create_category():
    """Uses OpenAI to generate a category from a natural language description."""
    data = request.get_json()
    user_input = data.get('description', '').strip()
    if not user_input:
        return jsonify({'error': 'Description required'}), 400

    existing_colors = [c.color for c in Category.query.filter_by(user_id=current_user.id).all()]

    prompt = (
        f'Create a task category based on: "{user_input}"\n'
        f'Existing colors (avoid these): {", ".join(existing_colors)}\n\n'
        f'Return ONLY a JSON object with keys: "name" (short clear name), '
        f'"color" (hex color, visually distinct from existing), '
        f'"icon" (a Font Awesome 6 icon class like fa-briefcase, fa-heart, fa-home, fa-code — class name only, no prefix).\n'
        f'Example: {{"name": "Work Projects", "color": "#7c3aed", "icon": "fa-briefcase"}}'
    )

    raw = openai_chat(
        prompt,
        system='You are a UI designer. Return only valid JSON.',
        max_tokens=100
    )

    try:
        # Extract JSON from response (handle markdown code blocks)
        if '```' in raw:
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
        category_data = json.loads(raw.strip())
        return jsonify({
            'name': category_data.get('name', 'New Category'),
            'color': category_data.get('color', '#3b82f6'),
            'icon': category_data.get('icon', 'fa-folder')
        })
    except Exception:
        return jsonify({'error': 'Could not parse AI response', 'raw': raw}), 500


@api.route('/api/categories/suggest-color', methods=['GET'])
@login_required
def suggest_color():
    """Suggests a color visually distinct from existing category colors."""
    existing_colors = [c.color for c in Category.query.filter_by(user_id=current_user.id).all()]

    if not existing_colors:
        return jsonify({'color': '#3b82f6'})

    prompt = (
        f'Existing colors: {", ".join(existing_colors)}\n'
        f'Suggest ONE hex color that is visually distinct from all of them, '
        f'professional-looking, and accessible. Reply with ONLY the hex code.'
    )
    color = openai_chat(prompt, system='You are a color expert. Reply with only a hex color code like #ff5733.')

    # Validate it looks like a hex color
    import re
    if re.match(r'^#[0-9a-fA-F]{6}$', color.strip()):
        return jsonify({'color': color.strip()})
    return jsonify({'color': '#8b5cf6'})  # fallback


@api.route('/api/categories/insights', methods=['GET'])
@login_required
def get_category_insights():
    """Returns smart insights about category usage."""
    categories = Category.query.filter_by(
        user_id=current_user.id, archived=False
    ).all()
    insights = []

    # Rule-based insights
    empty_cats = [c for c in categories if c.tasks.filter_by(deleted=False).count() == 0]
    if empty_cats:
        insights.append({
            'type': 'info',
            'icon': 'fa-folder-open',
            'message': f'{len(empty_cats)} empty {"category" if len(empty_cats) == 1 else "categories"}',
            'action': 'Consider adding tasks or deleting unused categories'
        })

    overloaded = [c for c in categories if c.tasks.filter_by(deleted=False).count() > 15]
    if overloaded:
        names = ', '.join(c.name for c in overloaded)
        insights.append({
            'type': 'warning',
            'icon': 'fa-triangle-exclamation',
            'message': f'"{names}" has many tasks',
            'action': 'Consider splitting into subcategories'
        })

    uncategorized_count = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == False,
        Task.deleted == False,
        ~Task.categories.any()
    ).count()
    if uncategorized_count > 3:
        insights.append({
            'type': 'suggestion',
            'icon': 'fa-lightbulb',
            'message': f'{uncategorized_count} tasks have no category',
            'action': 'Assign them to categories for better organisation'
        })

    # AI insight (optional, only if key is set)
    ai_suggestion = None
    if os.environ.get('OPENAI_API_KEY') and categories:
        task_titles = [
            t.title for t in Task.query.filter_by(
                user_id=current_user.id, completed=False, deleted=False
            ).limit(30).all()
        ]
        cat_names = [c.name for c in categories]
        if task_titles:
            prompt = (
                f'Current categories: {", ".join(cat_names)}\n'
                f'Recent tasks: {", ".join(task_titles[:20])}\n\n'
                f'In one short sentence, suggest ONE improvement to how these tasks are organised. '
                f'Be specific and actionable.'
            )
            ai_suggestion = openai_chat(
                prompt,
                system='You are a productivity coach. Give a short, actionable suggestion.',
                max_tokens=80
            )

    return jsonify({
        'insights': insights,
        'ai_suggestion': ai_suggestion
    })