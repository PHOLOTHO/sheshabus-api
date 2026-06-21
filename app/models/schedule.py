from app import db
from datetime import datetime

class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    day_type = db.Column(db.Enum('weekday', 'saturday', 'sunday', 'holiday', 'weekend'), nullable=False)
    first_bus = db.Column(db.Time, nullable=False)
    last_bus = db.Column(db.Time, nullable=False)
    frequency_minutes = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    route = db.relationship('Route', backref=db.backref('schedules', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'day_type': self.day_type,
            'first_bus': self.first_bus.isoformat() if self.first_bus else None,
            'last_bus': self.last_bus.isoformat() if self.last_bus else None,
            'frequency_minutes': self.frequency_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }