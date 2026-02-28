from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from app import mail
from app.forms import ForgotPasswordForm, LogInForm, SignUpForm, ResetPasswordForm


auth = Blueprint('auth', __name__)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    """Gets new user data and adds them to the database"""
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm_password = form.confirm_password.data

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

    return render_template('signup.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Logs in existing user"""
    form = LogInForm()
    if form.validate_on_submit:
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully.')
            return redirect(url_for('routes.index'))
        else:
            flash('Invalid credentials')

    return render_template('login.html', form=form)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Sends link to existing user for password reset"""
    form = ForgotPasswordForm()
    if form.validate_on_submit:
        email = form.email.data
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
    return render_template('forgot_password.html', form=form)


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Enables password reset"""
    email = confirm_token(token)  

    if not email:
        flash('Invalid or expired reset link.')
        return redirect(url_for('auth.forgot_password'))

    user = User.query.filter_by(email=email).first_or_404()
    
    form = ResetPasswordForm()
    if form.validate_on_submit:
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
    """logs out user"""
    session.clear()
    flash('Logged out.')
    return redirect(url_for('auth.login'))

def generate_token(email):
    """Generates password token"""
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='password-reset-salt')

def confirm_token(token, expiration=3600):
    """confirms password token"""
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
    except Exception:
        return None
    return email