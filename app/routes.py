from app import app
from flask import render_template, request, redirect

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
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
    return render_template('trash.html')

