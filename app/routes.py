from flask import flash, render_template, request, redirect, url_for
from flask import Blueprint
from app.models import Task
from . import db
from datetime import date, timedelta

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return render_template('index.html')

@routes.route('/tasks')
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

@routes.route('/trash')
def trash():
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_deleted = Task.query.filter(
        Task.deleted == True,
        Task.deleted_date == today
    ).all()

    yesterday_deleted = Task.query.filter(
        Task.deleted == True,
        Task.deleted_date == yesterday
    ).all()

    def summarize(task):
        total = len(task.subtasks)
        done = sum(1 for sub in task.subtasks if sub.completed)
        return f"{done}/{total} completed" if total > 0 else "Completed"

    for task in today_deleted + yesterday_deleted:
        task.category = "Home"
        task.color = "red"
        task.subtask_summary = summarize(task)

    return render_template(
        'trash.html',
        today_deleted=today_deleted,
        yesterday_deleted=yesterday_deleted,
        today_date=today.strftime("%B %d, %Y"),
        yesterday_date=yesterday.strftime("%B %d, %Y")
    )

@routes.route('/complete_task/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    task.completed_date = date.today()  
    db.session.commit()
    flash("Task marked as completed", "success")
    return redirect(url_for('routes.tasks'))

@routes.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.deleted = True
    task.deleted_date = date.today()  
    db.session.commit()
    flash("Task moved to trash", "success")
    return redirect(url_for('routes.tasks'))

@routes.route('/restore_tasks', methods=['POST'])
def restore_tasks():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.get(int(task_id))
        if task and task.deleted:
            task.deleted = False
            task.deleted_date = None
    db.session.commit()
    flash(f"{len(task_ids)} task(s) restored.", "success")
    return redirect(url_for('routes.trash'))

@routes.route('/delete_tasks_permanently', methods=['POST'])
def delete_tasks_permanently():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.get(int(task_id))
        if task and task.deleted:
            db.session.delete(task)
    db.session.commit()
    flash(f"{len(task_ids)} task(s) permanently deleted.", "success")
    return redirect(url_for('routes.trash'))

@routes.route("/reopen_task/<int:task_id>", methods=["POST"])
def reopen_task(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed = False
        task.completed_date = None
        db.session.commit()
    return redirect(url_for('routes.history'))

@routes.route('/reopen_tasks', methods=['POST'])
def reopen_tasks():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.get(int(task_id))
        if task and task.completed:
            task.completed = False
            task.completed_date = None
    db.session.commit()
    flash(f"{len(task_ids)} task(s) reopened.", "success")
    return redirect(url_for('routes.history'))

@routes.route('/soft_delete_tasks', methods=['POST'])
def soft_delete_tasks():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.get(int(task_id))
        if task and not task.deleted:
            task.deleted = True
            task.deleted_date = date.today()
    db.session.commit()
    flash(f"{len(task_ids)} task(s) moved to trash.", "success")
    return redirect(url_for('routes.history'))

@routes.route('/history_action', methods=['POST'], endpoint='history_action')
def history_action():
    task_ids = request.form.getlist('task_ids')
    action = request.form.get('action')

    if not task_ids:
        flash("No tasks selected.", "error")
        return redirect(url_for('routes.history'))

    if action == "reopen":
        for task_id in task_ids:
            task = Task.query.get(int(task_id))
            if task and task.completed:
                task.completed = False
                task.completed_date = None
        flash(f"{len(task_ids)} task(s) reopened and moved back to Ongoing Tasks.", "success")

    elif action == "trash":
        for task_id in task_ids:
            task = Task.query.get(int(task_id))
            if task and not task.deleted:
                task.deleted = True
                task.deleted_date = date.today()
        flash(f"{len(task_ids)} task(s) moved to trash.", "success")

    db.session.commit()
    return redirect(url_for('routes.history'))
