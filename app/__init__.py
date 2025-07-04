from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

db = SQLAlchemy()

def create_app():
    load_dotenv()  # Loads variables from .env

    app = Flask(__name__)
    app.secret_key = 'dev-secret-key'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import routes after app is created to avoid circular import
    from app.routes import routes
    from app.api_routes import api

    app.register_blueprint(routes)
    app.register_blueprint(api)

    # Create tables
    with app.app_context():
        db.create_all()

    return app
