from app import db
from datetime import datetime

class Bus(db.Model):
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(50), unique=True, nullable=False)
    # license_plate = db.Column(db.String(20), unique=True, nullable=False)  # ← REMOVE THIS LINE
    capacity = db.Column(db.Integer, default=0)
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    gps_device_id = db.Column(db.String(100), unique=True)
    status = db.Column(db.Enum('on_time', 'delayed', 'out_of_service'), default='on_time')
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'))
    driver_name = db.Column(db.String(100))
    current_lat = db.Column(db.Numeric(10,8))
    current_lng = db.Column(db.Numeric(11,8))
    speed = db.Column(db.Numeric(5,2))
    next_stop_id = db.Column(db.Integer, db.ForeignKey('stops.id'))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Relationships
    assignments = db.relationship('BusAssignment', backref='bus', lazy='dynamic')
    locations = db.relationship('BusLocation', backref='bus', lazy='dynamic')
    alerts = db.relationship('Alert', backref='bus', lazy='dynamic')

    def to_dict(self):
        return {
            'id': str(self.id),
            'plate_number': self.plate_number,
            # 'license_plate': self.license_plate,  # ← REMOVE THIS
            'capacity': self.capacity,
            'model': self.model,
            'year': self.year,
            'gps_device_id': self.gps_device_id,
            'status': self.status,
            'route_id': self.route_id,
            'driver_name': self.driver_name,
            'current_lat': float(self.current_lat) if self.current_lat else None,
            'current_lng': float(self.current_lng) if self.current_lng else None,
            'speed': float(self.speed) if self.speed else None,
            'next_stop_id': self.next_stop_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BusAssignment(db.Model):
    __tablename__ = 'bus_assignments'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=False)
    assignment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'route_id': self.route_id,
            'driver_id': self.driver_id,
            'assignment_date': self.assignment_date.isoformat() if self.assignment_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class BusLocation(db.Model):
    __tablename__ = 'bus_locations'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float)
    direction = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'direction': self.direction,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }