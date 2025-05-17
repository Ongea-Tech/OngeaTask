from app import app
from flask import render_template, request, redirect

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/trash')
def trash():
    return render_template('trash.html')