from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_cors import CORS
from flask_migrate import Migrate
from flask_socketio import SocketIO
from dotenv import load_dotenv

from app.config import Config

# Load environment variables FIRST
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
mail = Mail()
migrate = Migrate()
socketio = SocketIO()


def create_app(config_name='default'):
    from .config import config

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

    # Configure CORS
    CORS(app,
         origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    # Register blueprints (import inside function to avoid circular imports)
    from app.api.auth import auth_bp
    from app.api.users import users_bp
    from app.api.routes import routes_bp
    from app.api.buses import buses_bp
    from app.api.drivers import drivers_bp
    from app.api.alerts import alerts_bp
    from app.api.support import support_bp
    from app.api.surveys import surveys_bp
    from app.api.realtime import realtime_bp
    from app.api.trips import trips_bp
    from app.api.ratings import ratings_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(routes_bp, url_prefix='/api/routes')
    app.register_blueprint(buses_bp, url_prefix='/api/buses')
    app.register_blueprint(drivers_bp, url_prefix='/api/drivers')
    app.register_blueprint(alerts_bp, url_prefix='/api/alerts')
    app.register_blueprint(support_bp, url_prefix='/api/support')
    app.register_blueprint(surveys_bp, url_prefix='/api/surveys')
    app.register_blueprint(realtime_bp, url_prefix='/api/realtime')
    app.register_blueprint(trips_bp, url_prefix='/api/trips')
    app.register_blueprint(ratings_bp, url_prefix='/api/ratings', strict_slashes=False)

    return app