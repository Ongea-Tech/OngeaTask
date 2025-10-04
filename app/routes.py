from datetime import date, timedelta
from flask import flash, render_template, request, redirect, url_for
from flask import Blueprint
from app.models import Task, Category, Profile  
from . import db

routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    active_tasks = Task.query.filter(
        db.and_(
            Task.completed == False,
            Task.deleted == False
        )
    ).all()
    return render_template('index.html', tasks=active_tasks)


@routes.route('/login')
def login():
    return render_template('login.html')

@routes.route('/signup')
def signup():
    return render_template('signup.html')

@routes.route('/profile')
def profile():
    return render_template('profile.html')

@routes.route('/settings')
def settings():
    return render_template('settings.html')

@routes.route('/categories', methods=['GET'])
def categories():
    categories = Category.query.all()
    return render_template('categories.html')

@routes.route('/logout')
def logout():
    return render_template('logout.html')

@routes.route('/tasks', methods=['GET'])
def tasks():
    active_tasks = Task.get_active_tasks()
    print(f"Active tasks count: {len(active_tasks)}")
    return render_template('tasks.html', tasks=active_tasks)

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
@routes.route('/individual-task/<int:task_id>')
def individual(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('individual-task.html', task=task)

@routes.route('/complete/<int:task_id>', methods=['POST'])
def mark_completed_single(task_id):
    try:
        task = db.session.query(Task).with_for_update().get(task_id)
        task.completed = True
        task.completed_date = date.today()
        task.deleted = False
        task.deleted_date = None
        db.session.flush() 
        db.session.commit()
        db.session.expire_all()
        return redirect(url_for('routes.index')) 
    except Exception as e:
        db.session.rollback()
        flash("Error marking task as completed", "error")
        return redirect(url_for('routes.index'))

@routes.route('/trash_single/<int:task_id>', methods=['POST'])
def move_to_trash_single(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.deleted = True
        task.deleted_date = date.today()
        task.completed = False
        task.completed_date = None
        db.session.flush()
        db.session.commit()
        db.session.expire_all()
        return redirect(url_for('routes.trash')) 
    except Exception as e:
        db.session.rollback()
        flash("Error moving task to trash", "error")
        return redirect(url_for('routes.index'))

@routes.route('/mark-completed', methods=['POST'])
def mark_completed():
    task_id = request.form.get("task_id")

    if not task_id:
        flash("No task selected.", "error")
        return redirect(url_for("routes.index"))

    task = Task.query.get(task_id)
    if task:
        task.completed = True
        db.session.commit()
        flash("Task marked as completed!", "success")
    else:
        flash("Task not found!", "error")

    return redirect(url_for("routes.index"))
@routes.route('/individual-task')
def individual():
    return render_template('individual-task.html')



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

@routes.route('/history_action', methods=['POST'])
def history_action():
    action = request.form.get('action')
    task_ids = request.form.getlist('task_ids')

    if not task_ids:
        flash("No tasks selected.", "error")
        return redirect(url_for('routes.index'))

    for task_id in task_ids:
        task = Task.query.get(int(task_id))
        if not task:
            continue

        if action == 'reopen':
            task.completed = False
            task.completed_date = None
            task.deleted = False
            task.deleted_date = None
            db.session.flush()
            db.session.refresh(task)
        elif action == 'trash':
            task.move_to_trash()
        else:
            flash("Invalid action.", "error")
            return redirect(url_for('routes.history'))

    db.session.commit()
    db.session.expire_all()

    if action == 'reopen':
        flash(f"{len(task_ids)} task(s) reopened.", "success")
        return redirect(url_for('routes.history'))
    elif action == 'trash':
        flash(f"{len(task_ids)} task(s) moved to trash.", "success")

    return redirect(url_for('routes.history'))

@routes.route('/trash', methods=['GET'])
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

@routes.route('/restore_bulk', methods=['POST'])
def restore_bulk():
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

@routes.route('/move-to-trash', methods=['POST'])
def move_to_trash():
    try:
        ids = request.form.get('trash_ids', '')
        if ids:
            task_ids = [int(tid) for tid in ids.split(',')]
            for task_id in task_ids:
                task = Task.query.get(task_id)
                if task:
                    task.move_to_trash()
            db.session.commit()
            flash(f"Tasks moved to trash successfully", "success")
        return redirect(url_for('routes.index'))
    except Exception as e:
        db.session.rollback()
        print(f"Error moving tasks to trash: {str(e)}")
        flash("Error moving tasks to trash", "error")
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
