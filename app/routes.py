from app import app
from flask import render_template


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/individual')
def individual():
    return render_template('individual.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/trash')
def trash():
    return render_template('trash.html')

@app.route('/ongoing')
def ongoing():
    return render_template('ongoing.html')