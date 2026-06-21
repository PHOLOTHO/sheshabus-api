import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sheshabus-secret-key-2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-sheshabus'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    # Database Configuration
    if os.environ.get('FLASK_ENV') == 'production':
        # PostgreSQL for production (Supabase)
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgresql://'):
            # Replace postgresql:// with postgresql+psycopg2:// for SQLAlchemy
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'postgresql+psycopg2://')
    else:
        # MySQL for development
        db_password = quote_plus(os.environ.get('DB_PASSWORD') or 'password')
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL') or f'mysql+pymysql://root:{db_password}@localhost/sheshabus'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email Configuration
    EMAIL_HOST = os.environ.get('EMAIL_HOST') or "smtp.office365.com"
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
    EMAIL_USER = os.environ.get('EMAIL_USER') or "willcom.reporting@willcom.co.za"
    EMAIL_PASS = os.environ.get('EMAIL_PASS')

    # Flask-Mail configuration
    MAIL_SERVER = EMAIL_HOST
    MAIL_PORT = EMAIL_PORT
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = EMAIL_USER
    MAIL_PASSWORD = EMAIL_PASS
    MAIL_DEFAULT_SENDER = EMAIL_USER
    MAIL_DEBUG = False

    # Frontend URLs
    FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:5173'
    ADMIN_URL = os.environ.get('ADMIN_URL') or 'http://localhost:5001'

    # VAPID Keys
    VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY')
    VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY')

    # CORS Origins
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',') if os.environ.get('CORS_ORIGINS') else [
        'http://localhost:5173',
        'http://localhost:5001',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5001',
    ]

    # Redis Configuration (Optional)
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # Celery Configuration (Optional)
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'

    # Application Settings
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    MAIL_DEBUG = True
    MAIL_SUPPRESS_SEND = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    MAIL_DEBUG = False
    MAIL_SUPPRESS_SEND = False

    # In production, require these environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    EMAIL_PASS = os.environ.get('EMAIL_PASS')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MAIL_SUPPRESS_SEND = True
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Create upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)