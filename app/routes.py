from flask import render_template, request, redirect
from flask import Blueprint
from app.models import Task

routes = Blueprint('routes', __name__)

@routes.route('/', endpoint='index')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@routes.route('/tasks')
def tasks():
    tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

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

