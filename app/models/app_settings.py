# app/models/app_settings.py
from app import db
from datetime import datetime


class AppSettings(db.Model):
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True, default=1)
    contact_phone = db.Column(db.String(20))
    contact_email = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'contact_phone': self.contact_phone,
            'contact_email': self.contact_email
        }