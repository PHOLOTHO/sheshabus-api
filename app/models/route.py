from app import db
from datetime import datetime

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.Text)
    start_point = db.Column(db.String(255))
    end_point = db.Column(db.String(255))
    fare = db.Column(db.Numeric(10,2))
    path_geojson = db.Column(db.JSON)
    color = db.Column(db.String(7), default='#008080')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('admin_users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships - use string references to avoid circular imports
    stops = db.relationship('Stop', secondary='route_stops',
                            primaryjoin='Route.id == RouteStop.route_id',
                            secondaryjoin='RouteStop.stop_id == Stop.id',
                            order_by='RouteStop.sequence', viewonly=True)
    assignments = db.relationship('BusAssignment', backref='route', lazy='dynamic')
    favorites = db.relationship('UserFavorite', backref='route', lazy='dynamic')
    alerts = db.relationship('Alert', backref='route', lazy='dynamic')

    def to_dict(self, detailed=False):
        data = {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'description': self.description,
            'start_point': self.start_point,
            'end_point': self.end_point,
            'fare': str(self.fare) if self.fare else None,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if detailed:
            # Use RouteStop query directly to avoid recursion
            route_stops = db.session.query(RouteStop).filter_by(route_id=self.id).order_by(RouteStop.sequence).all()
            stops_data = []
            for rs in route_stops:
                stop = Stop.query.get(rs.stop_id)
                if stop:
                    stops_data.append({
                        **stop.to_dict(),
                        'sequence': rs.sequence,
                        'scheduled_time': rs.scheduled_time.isoformat() if rs.scheduled_time else None
                    })
            data['stops'] = stops_data
            data['path_geojson'] = self.path_geojson
        return data


class RouteStop(db.Model):
    __tablename__ = 'route_stops'
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey('stops.id'), primary_key=True)
    sequence = db.Column(db.Integer, nullable=False)
    scheduled_time = db.Column(db.Time)

    def to_dict(self):
        return {
            'route_id': self.route_id,
            'stop_id': self.stop_id,
            'sequence': self.sequence,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None
        }


class Stop(db.Model):
    __tablename__ = 'stops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    lat = db.Column(db.Numeric(10,8), nullable=False)
    lng = db.Column(db.Numeric(11,8), nullable=False)
    is_accessible = db.Column(db.Boolean, default=False)
    landmarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'lat': float(self.lat),
            'lng': float(self.lng),
            'is_accessible': self.is_accessible,
            'landmarks': self.landmarks
        }