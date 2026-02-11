from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Task, Subtask
from app.forms.history_forms import HistoryActionForm

routes = Blueprint('routes', __name__)


@routes.route('/')
def index():
    tasks = Task.get_active_tasks()
    return render_template('index.html', tasks=tasks)


@routes.route('/tasks')
def tasks():
    tasks = Task.get_active_tasks()
    return render_template('tasks.html', tasks=tasks)


@routes.route('/individual-task/<int:task_id>')
def individual(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('individual-task.html', task=task)


@routes.route('/create_task', methods=['POST'])
def create_task():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        flash("Task name is required", "error")
        return redirect(url_for('routes.index'))

    task = Task(title=name, description=description)
    db.session.add(task)
    db.session.commit()

    flash("Task created successfully", "success")
    return redirect(url_for('routes.individual', task_id=task.id))


@routes.route('/complete/<int:task_id>', methods=['POST'])
def mark_completed_single(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.mark_as_completed()
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Error completing task", "error")

    return redirect(url_for('routes.index'))


@routes.route('/trash_single/<int:task_id>', methods=['POST'])
def move_to_trash_single(task_id):
    try:
        task = Task.query.get_or_404(task_id)
        task.move_to_trash()
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash("Error moving task to trash", "error")

    return redirect(url_for('routes.trash'))


@routes.route('/mark-completed', methods=['POST'])
def mark_completed_bulk():
    ids = request.form.get('completed_ids', '')

    if ids:
        task_ids = [int(i) for i in ids.split(',')]
        for task_id in task_ids:
            task = Task.query.get(task_id)
            if task:
                task.mark_as_completed()

        db.session.commit()

    return redirect(url_for('routes.index'))


@routes.route('/move-to-trash', methods=['POST'])
def move_to_trash_bulk():
    ids = request.form.get('trash_ids', '')

    try:
        if ids:
            task_ids = [int(i) for i in ids.split(',')]
            for task_id in task_ids:
                task = Task.query.get(task_id)
                if task:
                    task.move_to_trash()

            db.session.commit()
            flash("Tasks moved to trash", "success")
    except Exception:
        db.session.rollback()
        flash("Error moving tasks", "error")

    return redirect(url_for('routes.index'))


@routes.route('/history')
def history():
    form = HistoryActionForm()

    today = date.today()
    yesterday = today - timedelta(days=1)

    today_tasks = Task.query.filter_by(
        completed=True,
        deleted=False,
        completed_date=today
    ).all()

    yesterday_tasks = Task.query.filter_by(
        completed=True,
        deleted=False,
        completed_date=yesterday
    ).all()

    return render_template(
        'history.html',
        form=form,
        today_tasks=today_tasks,
        yesterday_tasks=yesterday_tasks,
        today_date=today.strftime("%B %d, %Y"),
        yesterday_date=yesterday.strftime("%B %d, %Y")
    )


@routes.route('/history_action', methods=['POST'])
def history_action():
    form = HistoryActionForm()

    if not form.validate_on_submit():
        flash("Invalid request", "error")
        return redirect(url_for('routes.history'))

    action = form.action.data
    task_ids = [int(i) for i in form.task_ids.data.split(',') if i.isdigit()]

    for task_id in task_ids:
        task = Task.query.get(task_id)
        if not task:
            continue

        if action == 'reopen':
            task.completed = False
            task.completed_date = None
            task.deleted = False
            task.deleted_date = None
        elif action == 'trash':
            task.move_to_trash()

    db.session.commit()
    flash(f"{len(task_ids)} task(s) updated", "success")
    return redirect(url_for('routes.history'))


@routes.route('/trash')
def trash():
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_deleted = Task.query.filter_by(
        deleted=True,
        deleted_date=today
    ).all()

    yesterday_deleted = Task.query.filter_by(
        deleted=True,
        deleted_date=yesterday
    ).all()

    return render_template(
        'trash.html',
        today_deleted=today_deleted,
        yesterday_deleted=yesterday_deleted,
        today_date=today.strftime("%B %d, %Y"),
        yesterday_date=yesterday.strftime("%B %d, %Y")
    )


@routes.route('/restore_bulk', methods=['POST'])
def restore_bulk():
    ids = request.form.get('all_task_ids', '')
    task_ids = [int(i) for i in ids.split(',') if i.isdigit()]

    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and task.deleted:
            task.deleted = False
            task.deleted_date = None

    db.session.commit()
    flash(f"{len(task_ids)} task(s) restored", "success")
    return redirect(url_for('routes.trash'))


@routes.route('/delete_tasks_permanently', methods=['POST'])
def delete_tasks_permanently():
    ids = request.form.get('all_task_ids', '')
    task_ids = [int(i) for i in ids.split(',') if i.isdigit()]

    for task_id in task_ids:
        task = Task.query.get(task_id)
        if task and task.deleted:
            db.session.delete(task)

    db.session.commit()
    flash(f"{len(task_ids)} task(s) permanently deleted", "success")
    return redirect(url_for('routes.trash'))


@routes.route('/delete-selected', methods=['POST'])
def delete_selected():
    ids = request.form.get('delete_ids', '')
    subtask_ids = [int(i) for i in ids.split(',') if i.isdigit()]

    if subtask_ids:
        Subtask.query.filter(Subtask.id.in_(subtask_ids)).delete(
            synchronize_session=False
        )
        db.session.commit()

    return redirect(request.referrer or url_for('routes.index'))
