from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db  # This should work if db is properly exported
from app.models.trip import Trip
from app.models.route import Route
from app.models.bus import Bus
from app.models.rating import Rating
from datetime import datetime

trips_bp = Blueprint('trips', __name__)


@trips_bp.route('/', methods=['GET'])
@jwt_required()
def get_user_trips():
    try:
        user_id = get_jwt_identity()

        trips = Trip.query.filter_by(user_id=user_id) \
            .order_by(Trip.started_at.desc()).all()

        trips_data = []
        for trip in trips:
            trip_dict = {
                'id': trip.id,
                'route_id': trip.route_id,
                'bus_id': trip.bus_id,
                'fare': float(trip.fare) if trip.fare else None,
                'started_at': trip.started_at.isoformat() if trip.started_at else None,
                'ended_at': trip.ended_at.isoformat() if trip.ended_at else None
            }

            route = Route.query.get(trip.route_id)
            if route:
                trip_dict['route_name'] = route.name
                trip_dict['route_number'] = route.number

            if trip.bus_id:
                bus = Bus.query.get(trip.bus_id)
                if bus:
                    trip_dict['bus_number'] = bus.plate_number

            rating = Rating.query.filter_by(trip_id=trip.id).first()
            trip_dict['rating_given'] = rating is not None
            trip_dict['rating_stars'] = rating.stars if rating else None

            trips_data.append(trip_dict)

        return jsonify({'trips': trips_data}), 200

    except Exception as e:
        print(f"Error in get_user_trips: {str(e)}")
        return jsonify({'message': 'Failed to fetch trips', 'error': str(e)}), 500


@trips_bp.route('/<int:trip_id>/rate', methods=['POST'])
@jwt_required()
def rate_trip(trip_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        trip = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not trip:
            return jsonify({'message': 'Trip not found'}), 404

        existing = Rating.query.filter_by(trip_id=trip_id).first()
        if existing:
            return jsonify({'message': 'Trip already rated'}), 409

        rating = Rating(
            user_id=user_id,
            trip_id=trip_id,
            stars=data.get('stars', 5),
            cleanliness=data.get('cleanliness', 5),
            punctuality=data.get('punctuality', 5),
            driver=data.get('driver', 5),
            comment=data.get('comment')
        )

        db.session.add(rating)
        db.session.commit()

        return jsonify(rating.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in rate_trip: {str(e)}")
        return jsonify({'message': 'Failed to submit rating', 'error': str(e)}), 500