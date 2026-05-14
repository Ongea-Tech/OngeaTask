from datetime import date, timedelta
from flask import flash, render_template, request, redirect, url_for, Blueprint
from flask_login import current_user, login_required
from app.models import Task, User, Subtask, Category , Notification
from . import db, login_manager
from app.forms import TaskForm, MoveToTrashForm
from app.services.smart_reminder_service import (get_best_time_message, generate_smart_nudges_for_user)
from werkzeug.exceptions import Forbidden
from flask import abort
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

routes = Blueprint('routes', __name__)

@routes.route('/')
@login_required
def index():
    priority = request.args.get('priority')
    status = request.args.get('status')
    category_id = request.args.get('category')
    date_filter = request.args.get('date')
    today = date.today()

    query = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deleted == False
    )

    if priority:
        query = query.filter(Task.priority == priority)

    if category_id:
        query = query.filter(Task.category_id == category_id)

    if status == 'completed':
        query = query.filter(Task.completed == True)
    elif status == 'not_completed':
        query = query.filter(Task.completed == False)
    elif status == 'approaching':
        query = query.filter(
            Task.completed == False,
            Task.due_date != None,
            Task.due_date >= today,
            Task.due_date <= today + timedelta(days=3)
        )

    if date_filter == 'today':
        query = query.filter(Task.due_date == today)
    elif date_filter == 'this_week':
        query = query.filter(Task.due_date <= today + timedelta(days=7))
    elif date_filter == 'overdue':
        query = query.filter(Task.due_date < today, Task.completed == False)

    active_tasks = query.all()
    task_titles = [task.title for task in active_tasks]
    message = "You have no tasks today. Take time to reset and plan ahead."

    if task_titles:
        formatted_tasks = "\n".join([f"- {title}" for title in task_titles])
        prompt = f"""
        You are a motivational coach.
        A user has the following tasks:
        {formatted_tasks}
        Generate a short, encouraging motivational message (max 2 sentences).
        Make it personal, warm, and energizing.
        Avoid clichés.
        """
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            message = response.choices[0].message.content.strip()
        except Exception:
            message = "Start where you are. Do what you can. Keep going."

    current_user.motivation_message = message
    current_user.motivation_date = date.today()
    db.session.commit()

    categories = Category.query.all()

    return render_template(
        'index.html',
        tasks=active_tasks,
        form=TaskForm(),
        trash_form=MoveToTrashForm(),
        motivation_message=message,
        categories=categories
    )

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
    current_user.logger.info(
    f"Loaded tasks page for user_id={current_user.id}, active_tasks={len(active_tasks)}"
    ) 
    return render_template('tasks.html', tasks=active_tasks)

@routes.route('/<int:task_id>')
@login_required
def show_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    form = TaskForm()
    return render_template('individual-task.html', task=task, form=form)

@routes.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]
    if form.validate_on_submit():
    
        title = form.title.data
        description = form.description.data or None

        new_task = Task(title=title, description=description, completed=False, user_id=current_user.id, due_date=form.due_date.data, estimated_minutes=form.estimated_minutes.data, category_id=form.category_id.data if form.category_id.data else None)
        db.session.add(new_task)
        db.session.commit()

        # Auto-generate subtasks
        if form.auto_generate.data:
            subtasks = generate_subtasks_with_ai(title, description)

            for sub in subtasks:
                db.session.add(Subtask(title=sub, task_id=new_task.id))

            db.session.commit()

        flash('Task created successfully!', 'success')

        return redirect(url_for('routes.individual', task_id=new_task.id))
    
    return render_template('index.html', form=form)

@routes.route('/individual-task/<int:task_id>')
@login_required
def individual(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    form = TaskForm()
    return render_template('individual-task.html', task=task, form=form)

def generate_subtasks_with_ai(title, description=None):
    prompt = f"""
    You are a productivity assistant.

    Break down the following task, with its description, into 5-7 clear, actionable subtasks.

    Task Title: {title}
    Task Description: {description or "No description provided"}

    Rules:
    - Each subtask should be short and specific
    - Each should be something an individual can actually do
    - Return as a simple list (no numbering, no extra text)
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        content = response.choices[0].message.content.strip()

        # Convert response into list
        subtasks = [line.strip("- ").strip() for line in content.split("\n") if line.strip()]

        return subtasks

    except Exception as e:
        print("Subtask generation error:", str(e))
        return []
    
@routes.route('/api/tasks/<int:task_id>/subtasks', methods=['POST'])
@login_required
def add_subtask(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    title = data.get('title', '').strip()

    if not title:
        return {"message": "Subtask title cannot be empty."}, 400

    # Duplication protection
    existing_titles = {s.title.strip().lower() for s in task.subtasks}
    if title.lower() in existing_titles:
        return {"message": f'Subtask "{title}" already exists in this task.'}, 409

    subtask = Subtask(title=title, task_id=task.id, completed=False)
    db.session.add(subtask)
    db.session.commit()
    return {"message": "Subtask added.", "id": subtask.id}, 201

@routes.route('/generate_subtasks/<int:task_id>', methods=['POST'])
@login_required
def generate_subtasks(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()

    # Check if subtasks already exist, disable generation if so
    if task.subtasks:
        return {"message": "Subtasks already exist for this task."}, 400

    subtasks = generate_subtasks_with_ai(task.title, task.description)

    if not subtasks:
        return {"message": "Failed to generate subtasks. Please try again."}, 500

    # Duplication protection. Get existing titles (lowercase) for comparison
    existing_titles = {s.title.strip().lower() for s in task.subtasks}

    added = 0
    for sub in subtasks:
        clean = sub.strip()
        if clean and clean.lower() not in existing_titles:
            db.session.add(Subtask(title=clean, task_id=task.id))
            existing_titles.add(clean.lower())
            added += 1

    db.session.commit()

    return {
        "message": f"{added} subtasks generated successfully.",
        "disclaimer": "These subtasks were generated by AI. Please review and adjust them to fit your needs."
    }, 200

@routes.route('/edit_subtask/<int:subtask_id>', methods=['POST'])
def edit_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
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
    task.completed_at = date.today()
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
        task.completed_at = None

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
        Task.completed_at == today
    ).all()

    yesterday_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        Task.deleted == False,
        Task.completed_at == yesterday
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
            task.completed_at = None
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
    today = date.today()
    yesterday = today - timedelta(days=1)

    today_deleted = Task.query.filter(
        Task.user_id == current_user.id,
        Task.deleted == True,
        Task.deleted_date == today
    ).all()

    yesterday_deleted = Task.query.filter(
        Task.user_id == current_user.id,
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
@login_required
def restore_bulk():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.filter_by(id=int(task_id), user_id=current_user.id).first()
        if task and task.deleted:
            task.deleted = False
            task.deleted_date = None
    db.session.commit()
    flash(f"{len(task_ids)} task(s) restored.", "success")
    return redirect(url_for('routes.trash'))

@routes.route('/delete_tasks_permanently', methods=['POST'])
@login_required
def delete_tasks_permanently():
    task_ids = request.form.getlist('task_ids')
    for task_id in task_ids:
        task = Task.query.filter_by(id=int(task_id), user_id=current_user.id).first()
        if task and task.deleted:
            db.session.delete(task)
    db.session.commit()
    flash(f"{len(task_ids)} task(s) permanently deleted.", "success")
    return redirect(url_for('routes.trash'))

@routes.route('/move-to-trash', methods=['POST'])
@login_required
def move_to_trash():
    trashform = MoveToTrashForm()
    try:
        ids = request.form.get('trash_ids', '')

        if ids:
            task_ids = [int(tid) for tid in ids.split(',')]
            for task_id in task_ids:
                task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
                if task:
                    task.move_to_trash()

            db.session.commit()
            flash(f"Tasks moved to trash successfully", "success")
        return redirect(url_for('routes.index'), trash_form=trashform)
    except Exception as e:
        db.session.rollback()
        print(f"Error moving tasks to trash: {str(e)}")
        flash("Error moving tasks to trash", "error")
        return redirect(url_for('routes.index'))

@routes.route('/api/subtasks/<int:subtask_id>', methods=['DELETE'])
@login_required
def delete_subtask(subtask_id):
    subtask = Subtask.query.join(Task).filter(
        Subtask.id == subtask_id,
        Task.user_id == current_user.id
    ).first_or_404()
    db.session.delete(subtask)
    db.session.commit()
    return {"message": "Deleted."}, 200

@routes.route('/delete-selected', methods=['POST'])
@login_required
def delete_selected():
    ids_str = request.form.get('delete_ids', '')
    ids = [int(i.strip()) for i in ids_str.split(',') if i.strip().isdigit()]

    if ids:
        for subtask_id in ids:
            subtask = Subtask.query.join(Task).filter(
                Subtask.id == subtask_id,
                Task.user_id == current_user.id
            ).first()
            if subtask:
                db.session.delete(subtask)
        db.session.commit()

    return redirect(request.referrer or url_for('routes.index'))

@routes.route('/api/tasks/<int:task_id>/description', methods=['PATCH'])
@login_required
def update_description(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    data = request.get_json()
    task.description = data.get('description', task.description)
    db.session.commit()
    return {"message": "Updated."}, 200

@routes.route('/smart-reminders')
@login_required
def smart_reminders():
    best_time_message = get_best_time_message(current_user.id)
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(10).all()

    return render_template('smart_reminders.html', best_time_message = best_time_message, notifications=notifications)

@routes.route('/smart-reminders/generate', methods=['POST'])
@login_required
def generate_smart_reminders():
    generated = generate_smart_nudges_for_user(current_user.id)

    if generated:
        flash(f"{len(generated)} smart reminder(s) generated.", "success")
    else:
        flash("No smart reminders needed right now.", "info")
    return redirect(url_for('routes.smart_reminders'))    

@routes.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.read = True
    db.session.commit()
    return redirect(url_for('routes.smart_reminders')) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
