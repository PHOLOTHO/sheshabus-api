from app import db
from datetime import datetime


class Alert(db.Model):
    __tablename__ = 'alerts'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum('delay', 'cancel', 'emergency', 'info'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'))
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'))  # Add this line if missing
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    scheduled_for = db.Column(db.DateTime)
    sent_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    is_sent = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    # Relationships
    user_alerts = db.relationship('UserAlert', backref='alert', lazy='dynamic')
    # If you still want user_notifications, keep it; otherwise remove.
    user_notifications = db.relationship('UserNotification', backref='alert', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'body': self.body,
            'route_id': self.route_id,
            'bus_id': self.bus_id,
            'priority': self.priority,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'sent_by': self.sent_by,
            'is_sent': self.is_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class UserAlert(db.Model):
    __tablename__ = 'user_alerts'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), primary_key=True)
    read_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'alert_id': self.alert_id,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

# Keep UserNotification if needed (optional)
class UserNotification(db.Model):
    __tablename__ = 'user_notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'))
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'alert_id': self.alert_id,
            'title': self.title,
            'message': self.message,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }