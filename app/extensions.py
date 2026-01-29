from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login.login"

# @login_manager.user_loader
# def load_user(user_id):
#     # Flask-Login passes the user_id from session
#     return User.query.get(int(user_id))

