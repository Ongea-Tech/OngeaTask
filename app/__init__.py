# app/__init__.py
from flask import Flask
from dotenv import load_dotenv
import os

from app.extensions import db, login_manager

def create_app():
    load_dotenv()  # Loads .env

    app = Flask(__name__)
    app.secret_key = "dev-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models (so SQLAlchemy knows about them)
    from app.model_tables.login import User
    # from app.model_tables.subtask import Subtask
    # from app.models import Task
    

    # Register user_loader AFTER User import
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from app.routes import routes
    from app.api_routes import api
    from app.blueprints.login import login_bp
    from app.blueprints.subtask import subtasks_bp

    app.register_blueprint(routes)
    app.register_blueprint(api)
    app.register_blueprint(login_bp)
    app.register_blueprint(subtasks_bp)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
