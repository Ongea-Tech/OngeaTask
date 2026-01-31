from flask import flash, render_template, request, redirect, url_for, jsonify
from flask import Blueprint
from app.models import Task, Subtask
from app.services.individual_task_service import (get_individual_task, create_subtask, get_task_progress)
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/tasks', methods=['GET'])
def tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)


@routes.route('/create_task', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash("Task name is required", "error")
            return redirect(url_for('routes.create_task'))

        new_task = Task(title=name, description=description, completed=False)
        db.session.add(new_task)
        db.session.commit()

        flash("Task created successfully", "success")
        # Redirect to the newly created task page using its ID
        return redirect(url_for('routes.individual', task_id=new_task.id))

    return render_template('index.html')


# @routes.route('/login')
# def login():
#     return render_template('login.html')

@routes.route('/signup')
def signup():
    return render_template('signup.html')

@routes.route('/profile')
def profile():
    return render_template('profile.html')

@routes.route('/categories')
def categories():
    return render_template('categories.html')

@routes.route('/history')
def history():
    return render_template('history.html')

@routes.route('/logout')
def logout():
    return render_template('logout.html')

@routes.route('/individual-task/<int:task_id>')
def individual(task_id):
    task = Task.query.get_or_404(task_id)
    subtasks = Subtask.query.filter_by(task_id=task_id).all()
    progress = get_task_progress(task, subtasks)
    

    

    return render_template(
        "individual-task.html",
        task=task,
        subtasks=subtasks,
        progress=progress
    )


@routes.route('/settings')
def settings():
    return render_template('settings.html')

@routes.route('/trash')
def trash():
    return render_template('trash.html')

@routes.route("/mark_completed", methods=["POST"])
def mark_completed():
    data = request.get_json() or request.form
    completed_ids = data.get("completed_ids")

    if not completed_ids:
        return jsonify({"success": False, "message": "No subtasks selected"}), 400

    # Convert string IDs to integers if needed
    if isinstance(completed_ids, str):
        completed_ids = [int(i) for i in completed_ids.split(",")]
    else:
        completed_ids = [int(i) for i in completed_ids]

    # Update all selected subtasks
    for subtask_id in completed_ids:
        subtask = Subtask.query.get(subtask_id)
        if subtask:
            subtask.completed = True
            db.session.add(subtask)

    db.session.commit()

    # Recalculate progress for the task
    task_id = Subtask.query.get(completed_ids[0]).task_id
    task = Task.query.get(task_id)
    subtasks = Subtask.query.filter_by(task_id=task.id).all()
    progress = get_task_progress(task, subtasks)

    return jsonify({"success": True, "progress": progress})


@routes.route('/move-to-trash', methods=['POST'])
def move_to_trash():
    ids = request.form.get('trash_ids', '')
    if ids:
        task_ids = [int(tid) for tid in ids.split(',')]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                db.session.delete(task)
        db.session.commit()
    return redirect(url_for('routes.index'))

@routes.route('/delete-selected', methods=['POST'])
def delete_selected():
    ids_str = request.form.get('delete_ids', '')
    ids = [int(id.strip()) for id in ids_str.split(',') if id.strip().isdigit()]

    if ids:
        from app.models import Subtask
        Subtask.query.filter(Subtask.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()

    return redirect(request.referrer or url_for('routes.index'))
