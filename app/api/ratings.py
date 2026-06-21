from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.rating import Rating
from app.models.trip import Trip
from datetime import datetime

ratings_bp = Blueprint('ratings', __name__)


@ratings_bp.route('/', methods=['GET'])
@ratings_bp.route('', methods=['GET'])
@jwt_required()
def get_user_ratings():
    try:
        user_id = get_jwt_identity()

        ratings = Rating.query.filter_by(user_id=user_id) \
            .order_by(Rating.created_at.desc()).all()

        return jsonify({
            'ratings': [rating.to_dict() for rating in ratings]
        }), 200

    except Exception as e:
        print(f"Error in get_user_ratings: {str(e)}")
        return jsonify({'message': 'Failed to fetch ratings', 'error': str(e)}), 500


@ratings_bp.route('/', methods=['POST'])
@ratings_bp.route('', methods=['POST'])
@jwt_required()
def create_rating():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        trip = Trip.query.filter_by(id=data['trip_id'], user_id=user_id).first()
        if not trip:
            return jsonify({'message': 'Trip not found'}), 404

        existing = Rating.query.filter_by(trip_id=data['trip_id']).first()
        if existing:
            return jsonify({'message': 'Trip already rated'}), 409

        rating = Rating(
            user_id=user_id,
            trip_id=data['trip_id'],
            stars=data['stars'],
            cleanliness=data['cleanliness'],
            punctuality=data['punctuality'],
            driver=data['driver'],
            comment=data.get('comment')
        )

        db.session.add(rating)
        db.session.commit()

        return jsonify(rating.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in create_rating: {str(e)}")
        return jsonify({'message': 'Failed to submit rating', 'error': str(e)}), 500


@ratings_bp.route('/trip/<int:trip_id>', methods=['GET'])
@ratings_bp.route('/trip/<int:trip_id>/', methods=['GET'])
@jwt_required()
def check_trip_rating(trip_id):
    try:
        user_id = get_jwt_identity()
        rating = Rating.query.filter_by(trip_id=trip_id, user_id=user_id).first()
        return jsonify({'exists': rating is not None}), 200
    except Exception as e:
        print(f"Error in check_trip_rating: {str(e)}")
        return jsonify({'message': 'Failed to check rating', 'error': str(e)}), 500