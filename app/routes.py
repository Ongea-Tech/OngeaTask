from datetime import date, timedelta
from flask import flash, render_template, request, redirect, url_for
from flask import Blueprint
from app.models import Task
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/tasks', methods=['GET'])
def tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@routes.route('/<int:task_id>')
def show_task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('individual-task.html', task=task)

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
        return redirect(url_for('routes.show_task', task_id=new_task.id))

    return render_template('index.html')


@routes.route('/login')
def login():
    return render_template('login.html')

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
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_tasks = Task.query.filter(
        Task.completed == True,
        Task.deleted == False,
        Task.completed_date == today
    ).all()

    yesterday_tasks = Task.query.filter(
        Task.completed == True,
        Task.deleted == False,
        Task.completed_date == yesterday
    ).all()

    def summarize(task):
        total = len(task.subtasks)
        done = sum(1 for sub in task.subtasks if sub.completed)
        return f"{done}/{total} completed" if total > 0 else "Completed"

    for task in today_tasks + yesterday_tasks:
        task.category = "Home"
        task.color = "red"
        task.subtask_summary = summarize(task)

    return render_template(
        'history.html',
        today_tasks=today_tasks,
        yesterday_tasks=yesterday_tasks,
        today_date=today.strftime("%B %d, %Y"),
        yesterday_date=yesterday.strftime("%B %d, %Y")
    )

@routes.route('/logout')
def logout():
    return render_template('logout.html')

@routes.route('/individual-task')
def individual():
    return render_template('individual-task.html')

@routes.route('/settings')
def settings():
    return render_template('settings.html')

@routes.route('/trash', methods=['GET'])
def trash():
    tasks = Task.query.filter_by(deleted=True).all()
    today = date.today()
    return render_template('trash.html', tasks=tasks, today=today)

@routes.route('/trash/<int:task_id>', methods=['POST'])
def restore_tasks(task_id):
    task = Task.query.get_or_404(task_id)
    task.deleted = False
    task.deleted_date = None
    db.session.commit()
    flash("Task restored successfully", "success")
    return redirect(url_for('routes.trash'))

@routes.route('/mark-completed', methods=['POST'])
def mark_completed():
    ids = request.form.get('completed_ids', '')
    if ids:
        task_ids = [int(tid) for tid in ids.split(',')]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                task.completed = True
        db.session.commit()
    return redirect(url_for('routes.index'))

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