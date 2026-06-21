from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    is_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100))
    reset_token = db.Column(db.String(100))
    reset_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    favorites = db.relationship('UserFavorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    support_tickets = db.relationship('SupportTicket', backref='user', lazy='dynamic')
    survey_responses = db.relationship('SurveyResponse', backref='user', lazy='dynamic')
    notifications = db.relationship('UserNotification', backref='user', lazy='dynamic')
    user_alerts = db.relationship('UserAlert', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class AdminUser(db.Model):
    __tablename__ = 'admin_users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_type = db.Column(db.Enum('1', '2', '3'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_routes = db.relationship('Route', backref='creator', lazy='dynamic')
    sent_alerts = db.relationship('Alert', backref='sender', lazy='dynamic')
    survey_created = db.relationship('Survey', backref='creator', lazy='dynamic')
    ticket_responses = db.relationship('SupportTicket', backref='responder', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role_type': self.role_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserFavorite(db.Model):
    __tablename__ = 'favorites'
    # Composite primary key – no 'id' column
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'route_id': self.route_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }