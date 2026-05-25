from datetime import date, timedelta
from flask import flash, jsonify, render_template, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from app.models import Task, User, Subtask
from . import db, login_manager
from app.forms import TaskForm, MoveToTrashForm
from werkzeug.exceptions import Forbidden
from flask import abort
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

routes = Blueprint('routes', __name__)

@routes.route('/test-500')
def test_500():
    raise Exception("Testing my awesome new 500 animation!")

@routes.route('/test-403')
def test_403():
    raise Forbidden("You don't have the secret pencil to enter here.")

@routes.route('/test-401')
def test_401():
    abort(401)

@routes.route('/')
@login_required
def index():
    active_tasks = Task.query.filter(
        db.and_(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.deleted == False
        )
    ).all()

    task_titles = [task.title for task in active_tasks]

    # daily cache
    if current_user.motivation_message and current_user.motivation_date == date.today():
        message = current_user.motivation_message

    else:
        if len(task_titles) >= 8:
            tone = "The user has many tasks and may feel overwhelmed. Use a calm, reassuring tone."
        elif len(task_titles) == 1:
            tone = "The user has one task. Use a focused, confident tone."
        else:
            tone = "Use a warm, balanced encouraging tone."

        if task_titles:
            formatted_tasks = "\n".join([f"- {title}" for title in task_titles])

            prompt = f"""
You are a motivational coach.

The user's name is {current_user.first_name}.

The user has the following tasks:
{formatted_tasks}

{tone}

Generate a short, personal motivational message (max 2 sentences).
Include the user's name naturally.
Avoid clichés.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4.1-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                message = response.choices[0].message.content.strip()

            except Exception:
                message = f"Start where you are, {current_user.first_name}. Keep going."

        else:
            message = f"{current_user.first_name}, you have no tasks today. Take time to reset and plan ahead."

        current_user.motivation_message = message
        current_user.motivation_date = date.today()
        db.session.commit()

    return render_template(
        'index.html',
        tasks=active_tasks,
        form=TaskForm(),
        trash_form=MoveToTrashForm(),
        motivation_message=message
    )

@routes.route('/regenerate-motivation', methods=['POST'])
@login_required
def regenerate_motivation():
    active_tasks = Task.query.filter(
        db.and_(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.deleted == False
        )
    ).all()

    task_titles = [task.title for task in active_tasks]

    if len(task_titles) >= 8:
        tone = "The user has many tasks and may feel overwhelmed. Use a calm, reassuring tone."
    elif len(task_titles) == 1:
        tone = "The user has one task. Use a focused, confident tone."
    else:
        tone = "Use a warm, balanced encouraging tone."

    if task_titles:
        formatted_tasks = "\n".join([f"- {title}" for title in task_titles])

        prompt = f"""
You are a motivational coach.

The user's name is {current_user.first_name}.

The user has the following tasks:
{formatted_tasks}

{tone}

Generate a short, personal motivational message (max 2 sentences).
Include the user's name naturally.
Avoid clichés.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            message = response.choices[0].message.content.strip()

        except Exception:
            message = f"Keep going, {current_user.first_name}."

    else:
        message = f"{current_user.first_name}, you have no tasks today. Reset and plan ahead."

    current_user.motivation_message = message
    current_user.motivation_date = date.today()
    db.session.commit()

    flash("Motivation regenerated.", "success")
    return redirect(url_for('routes.index'))

@routes.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@routes.route('/signup')
def signup():
    return render_template('signup.html')

@routes.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@routes.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

@routes.route('/categories')
@login_required
def categories():
    return render_template('categories.html')

@routes.route('/logout')
@login_required
def logout():
    return render_template('logout.html')

@routes.route('/tasks', methods=['GET'])
@login_required
def tasks():
    active_tasks = Task.query.filter(
        db.and_(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.deleted == False
        )
    ).all()
    return render_template('tasks.html', tasks=active_tasks)

@routes.route('/<int:task_id>')
@login_required
def show_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return render_template('individual-task.html', task=task)

@routes.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
    
        title = form.title.data
        description = form.description.data or None

        new_task = Task(title=title, description=description, completed=False, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('routes.individual', task_id=new_task.id))
    return render_template('index.html', form=form)

@routes.route('/individual-task/<int:task_id>')
@login_required
def individual(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    return render_template('individual-task.html', task=task)

@routes.route('/edit_subtask/<int:subtask_id>', methods=['POST'])
def edit_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(id)
    new_title = request.json.get('title')
    
    if new_title:
        subtask.title = new_title
        db.session.commit() # This saves it permanently
        return {"message": "Success"}, 200
    return {"message": "Content cannot be empty"}, 400

@routes.route('/complete/<int:task_id>', methods=['POST'])
@login_required
def mark_completed_single(task_id):

    task = db.session.query(Task).with_for_update().filter_by(
        id=task_id,
        user_id=current_user.id
    ).first_or_404()

    task.completed = True
    task.completed_date = date.today()
    task.deleted = False
    task.deleted_date = None

    db.session.commit()
    flash("Task marked as completed.", "success")
    return redirect(url_for('routes.index')) 
    

@routes.route('/trash_single/<int:task_id>', methods=['POST'])
@login_required
def move_to_trash_single(task_id):
    trashform = MoveToTrashForm()    
    try:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

        task.deleted = True
        task.deleted_date = date.today()
        task.completed = False
        task.completed_date = None

        db.session.commit()
        flash("Task moved to trash.", "success")
        return redirect(url_for('routes.trash')) 
    except Exception as e:
        db.session.rollback()
        flash("Error moving task to trash", "error")
        return redirect(url_for('routes.index'), trash_form=trashform)

@routes.route('/mark-completed', methods=['POST'])
@login_required
def mark_completed():
    ids = request.form.get('completed_ids', '')
    if ids:
        task_ids = [int(tid) for tid in ids.split(',')]
        for task_id in task_ids:
            task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
            if task:
                task.mark_as_completed()
               
        db.session.commit()
        flash("Task(s) marked as completed.", "success")

    return redirect(url_for('routes.index'))

@routes.route('/history')
@login_required
def history():
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        Task.deleted == False,
        Task.completed_date == today
    ).all()

    yesterday_tasks = Task.query.filter(
        Task.user_id == current_user.id,
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
@login_required
def history_action():
    action = request.form.get('action')
    task_ids = request.form.getlist('task_ids')

    if not task_ids:
        flash("No tasks selected.", "error")
        return redirect(url_for('routes.index'))

    for task_id in task_ids:
        task = Task.query.filter_by(id=int(task_id), user_id=current_user.id).first()
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
@login_required
def trash():
    # Show all deleted tasks, regardless of date
    all_deleted = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deleted == True
    ).all()
    def summarize(task):
        total = len(task.subtasks)
        done = sum(1 for sub in task.subtasks if sub.completed)
        return f"{done}/{total} completed" if total > 0 else "Completed"
    for task in all_deleted:
        task.category = "Home"
        task.color = "red"
        task.subtask_summary = summarize(task)
    return render_template(
        'trash.html',
        all_deleted=all_deleted
    )

@routes.route('/restore_bulk', methods=['POST'])
@login_required
def restore_bulk():
    task_ids = [int(task_id) for task_id in request.form.getlist('task_ids') if task_id.isdigit()]
    restored_count = 0
    for task_id in task_ids:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if task and task.deleted:
            task.deleted = False
            task.deleted_date = None
            restored_count += 1
    db.session.commit()
    if restored_count:
        flash(f"{restored_count} task(s) restored.", "success")
    else:
        flash("No deleted tasks were selected to restore.", "warning")
    return redirect(url_for('routes.trash'))

@routes.route('/delete_tasks_permanently', methods=['POST'])
@login_required
def delete_tasks_permanently():
    task_ids = [int(task_id) for task_id in request.form.getlist('task_ids') if task_id.isdigit()]
    deleted_count = 0
    for task_id in task_ids:
        task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
        if task and task.deleted:
            db.session.delete(task)
            deleted_count += 1
    db.session.commit()
    if deleted_count:
        flash(f"{deleted_count} task(s) permanently deleted.", "success")
    else:
        flash("No tasks were deleted. Please select tasks in the trash to delete.", "warning")
    return redirect(url_for('routes.trash'))

@routes.route('/move-to-trash', methods=['POST'])
@login_required
def move_to_trash():
    ids = request.form.get('trash_ids', '')

    if ids:
        try:
            task_ids = [int(tid) for tid in ids.split(',') if tid.strip()]
        except ValueError:
            flash("Invalid task IDs.", "danger")
            return redirect(url_for('routes.index'))

        for task_id in task_ids:
            task = Task.query.filter_by(
                id=task_id,
                user_id=current_user.id
            ).first()

            if task:
                task.move_to_trash()

        db.session.commit()
        flash("Task(s) moved to trash.", "success")
    else:
        flash("No tasks selected to move to trash.", "warning")

    return redirect(url_for('routes.index'))

@routes.route('/api/move-to-trash', methods=['POST'])
@login_required
def api_move_to_trash():
    data = request.get_json(silent=True) or {}
    raw_ids = data.get('task_ids', [])

    task_ids = []
    for task_id in raw_ids:
        try:
            task_ids.append(int(task_id))
        except (TypeError, ValueError):
            continue

    if not task_ids:
        return jsonify({'error': 'No valid task IDs provided.'}), 400

    tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.id.in_(task_ids),
        Task.deleted == False
    ).all()

    for task in tasks:
        task.move_to_trash()

    db.session.commit()

    return jsonify({
        'message': f'{len(tasks)} task(s) moved to trash.',
        'moved_ids': [task.id for task in tasks]
    }), 200
    
@routes.route('/delete-selected', methods=['POST'])
@login_required
def delete_selected():
    ids_str = request.form.get('delete_ids', '')
    ids = [int(id.strip()) for id in ids_str.split(',') if id.strip().isdigit()]

    if ids:
        from app.models import Subtask
        Subtask.query.join(Task).filter(
            Subtask.id.in_(ids),
            Task.user_id == current_user.id
        ).delete(synchronize_session=False)
        db.session.commit()

    return redirect(request.referrer or url_for('routes.index'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
