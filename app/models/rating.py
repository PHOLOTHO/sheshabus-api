from app import db
from datetime import datetime

class Rating(db.Model):
    __tablename__ = 'ratings'
    __table_args__ = {'extend_existing': True}  # Add this line

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False, unique=True)
    stars = db.Column(db.Integer, nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    punctuality = db.Column(db.Integer, nullable=False)
    driver = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    edit_deadline = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'trip_id': self.trip_id,
            'stars': self.stars,
            'cleanliness': self.cleanliness,
            'punctuality': self.punctuality,
            'driver': self.driver,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'edit_deadline': self.edit_deadline.isoformat() if self.edit_deadline else None
        }