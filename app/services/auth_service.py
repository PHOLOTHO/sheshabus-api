import jwt
from datetime import datetime, timedelta
from app import db
from app.models.user import User, AdminUser


class AuthService:
    @staticmethod
    def generate_verification_token():
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def generate_reset_token():
        import secrets
        return secrets.token_urlsafe(32)

    @staticmethod
    def validate_password_strength(password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        return True, "Password is strong"

    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_admin_by_email(email):
        return AdminUser.query.filter_by(email=email, is_active=True).first()