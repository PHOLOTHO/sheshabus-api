from app import db
from datetime import datetime


class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False, default='')  # Add this
    category = db.Column(db.Enum('technical', 'service', 'safety', 'suggestion', 'other'))
    status = db.Column(db.Enum('open', 'in_progress', 'resolved', 'closed'), default='open')
    priority = db.Column(db.Enum('low', 'medium', 'high'), default='medium')
    admin_response = db.Column(db.Text)
    responded_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    responded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = db.relationship('TicketMessage', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'category': self.category,
            'status': self.status,
            'priority': self.priority,
            'admin_response': self.admin_response,
            'responded_by': self.responded_by,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'messages': [msg.to_dict() for msg in self.messages.order_by(TicketMessage.created_at).all()]
        }

class TicketMessage(db.Model):
    __tablename__ = 'ticket_messages'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'sender_id': self.sender_id,
            'body': self.body,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_role = db.Column(db.Enum('commuter', 'support', 'admin'),
                            nullable=False)  # Changed from 'user' to 'commuter'
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'sender_role': self.sender_role,
            'body': self.body,
            'created_at': self.created_at.isoformat()
        }