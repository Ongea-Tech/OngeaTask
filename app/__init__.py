from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from flask_mail import Mail 


db = SQLAlchemy()
mail = Mail()
def create_app():
    load_dotenv()  # Loads variables from .env

    app = Flask(__name__)
    app.secret_key = 'dev-secret-key'

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    mail.init_app(app)
    

    # Import routes after app is created to avoid circular import
    from app.routes import routes
    from app.api_routes import api
    from app.auth_routes import auth

    app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD")
    
)
    mail.init_app(app)

    app.register_blueprint(routes)
    app.register_blueprint(api)
    app.register_blueprint(auth, url_prefix = '/auth')

    # Create tables
    with app.app_context():
        db.create_all()

    return app
