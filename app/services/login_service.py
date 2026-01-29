 # app/services/login_service.py
from app.model_tables.login import User
from app.extensions import db
from flask_login import login_user, logout_user
from itsdangerous import URLSafeTimedSerializer
from flask import current_app

class LoginService:
    """Service class for handling login, authentication, and password management."""

    # ---------- Authentication ----------
    @staticmethod
    def authenticate(email_or_username: str, password: str) -> User | None:
        """
        Authenticate a user by email or username.
        Returns the User object if credentials are correct, else None.
        """
        user = User.query.filter_by(email=email_or_username).first()
        if not user:
            user = User.query.filter_by(username=email_or_username).first()

        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def login(user: User):
        """Log in a user using Flask-Login."""
        login_user(user)

    @staticmethod
    def logout():
        """Log out the current user using Flask-Login."""
        logout_user()

    # ---------- Password Reset ----------
    @staticmethod
    def generate_reset_token(user: User) -> str:
        """
        Generate a secure token for password reset.
        Use itsdangerous serializer.
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return serializer.dumps(user.id, salt='password-reset-salt')

    @staticmethod
    def verify_reset_token(token: str, expiration: int = 3600) -> User | None:
        """
        Verify the password reset token.
        Returns the User object if valid, else None.
        """
        serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
        except Exception:
            return None
        return User.query.get(user_id)

    @staticmethod
    def update_password(user: User, new_password: str):
        """
        Update a user's password and commit to DB.
        """
        user.set_password(new_password)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    # ---------- Two-Factor Authentication (2FA) Placeholder ----------
    @staticmethod
    def verify_2fa(user: User, code: str) -> bool:
        """
        Placeholder method for verifying a 2FA code (TOTP, SMS, or email).
        Returns True if valid, False otherwise.
        """
        # Implement your TOTP or code verification logic here, e.g., using pyotp
        # Example:
        # import pyotp
        # totp = pyotp.TOTP(user.otp_secret)
        # return totp.verify(code)
        return True  # Temporary, always returns True for now

    @staticmethod
    def send_2fa_code(user: User):
        """
        Placeholder method to send a 2FA code via email or SMS.
        Implement using Flask-Mail or other service.
        """
        pass  # Replace with your email/SMS sending logic
