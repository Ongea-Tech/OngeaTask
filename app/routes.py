from flask import flash, render_template, request, redirect, url_for
from flask import Blueprint
from app.models import Task
from . import db

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
    return render_template('history.html')

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
    return render_template('trash.html')

