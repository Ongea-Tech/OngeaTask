from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from app import mail


auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth.signup'))

        new_user = User(username=username, first_name=first_name,
                        last_name=last_name, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Account created. Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully.')
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid credentials')

    return render_template('login.html')

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            msg = Message("Password Reset",
              sender="your-email@gmail.com",
              recipients=[user.email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            mail.send(msg)

            flash('password reset link has been sent to your email.')
            return redirect(url_for('auth.login'))
        else:
            flash('No account found with that email.')
    return render_template('forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token)  

    if not email:
        flash('Invalid or expired reset link.')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()

    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash('Passwords do not match.')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash('Password reset successful. Please log in.')
            return redirect(url_for('auth.login'))

    return render_template('reset_password.html', user=user)

@auth.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('auth.login'))

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='password-reset-salt')

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email