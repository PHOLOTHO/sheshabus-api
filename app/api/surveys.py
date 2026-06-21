from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.survey import Survey, SurveyResponse
from app.models.trip import Trip
from app.models.rating import Rating
from datetime import datetime

surveys_bp = Blueprint('surveys', __name__)


@surveys_bp.route('/', methods=['GET'])
@jwt_required()
def get_surveys():
    try:
        user_id = get_jwt_identity()
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        query = Survey.query
        if active_only:
            query = query.filter_by(is_active=True)

        surveys = query.all()

        survey_data = []
        for survey in surveys:
            survey_dict = survey.to_dict()
            existing_response = SurveyResponse.query.filter_by(
                survey_id=survey.id, user_id=user_id
            ).first()
            survey_dict['has_responded'] = existing_response is not None
            survey_data.append(survey_dict)

        return jsonify({'surveys': survey_data}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch surveys', 'error': str(e)}), 500


@surveys_bp.route('/<int:survey_id>', methods=['GET'])
@jwt_required()
def get_survey(survey_id):
    try:
        survey = Survey.query.get_or_404(survey_id)

        if not survey.is_active:
            return jsonify({'message': 'Survey is not active'}), 400

        return jsonify({'survey': survey.to_dict()}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch survey', 'error': str(e)}), 500


@surveys_bp.route('/<int:survey_id>/respond', methods=['POST'])
@jwt_required()
def submit_survey_response(survey_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        survey = Survey.query.get_or_404(survey_id)

        if not survey.is_active:
            return jsonify({'message': 'Survey is not active'}), 400

        existing_response = SurveyResponse.query.filter_by(
            survey_id=survey_id, user_id=user_id
        ).first()

        if existing_response:
            return jsonify({'message': 'You have already responded to this survey'}), 400

        response = SurveyResponse(
            survey_id=survey_id,
            user_id=user_id,
            rating=data.get('rating'),
            comment=data.get('comment')
        )

        db.session.add(response)
        db.session.commit()

        return jsonify({
            'message': 'Survey response submitted successfully',
            'response': response.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to submit survey response', 'error': str(e)}), 500


@surveys_bp.route('/responses', methods=['GET'])
@jwt_required()
def get_user_responses():
    try:
        user_id = get_jwt_identity()

        responses = SurveyResponse.query.filter_by(user_id=user_id) \
            .order_by(SurveyResponse.created_at.desc()).all()

        return jsonify({'responses': [response.to_dict() for response in responses]}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch survey responses', 'error': str(e)}), 500


# ===== RATINGS ENDPOINTS =====

@surveys_bp.route('/ratings', methods=['POST'])
@jwt_required()
def create_rating():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Check if trip exists and belongs to user
        trip = Trip.query.filter_by(id=data['trip_id'], user_id=user_id).first()
        if not trip:
            return jsonify({'message': 'Trip not found'}), 404

        # Check if already rated
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
        return jsonify({'message': 'Failed to submit rating', 'error': str(e)}), 500


@surveys_bp.route('/ratings/trip/<int:trip_id>', methods=['GET'])
@jwt_required()
def check_trip_rating(trip_id):
    try:
        user_id = get_jwt_identity()
        rating = Rating.query.filter_by(trip_id=trip_id, user_id=user_id).first()
        return jsonify({'exists': rating is not None}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to check rating', 'error': str(e)}), 500


@surveys_bp.route('/ratings', methods=['GET'])
@jwt_required()
def get_user_ratings():
    try:
        user_id = get_jwt_identity()
        ratings = Rating.query.filter_by(user_id=user_id) \
            .order_by(Rating.created_at.desc()).all()
        return jsonify({'ratings': [rating.to_dict() for rating in ratings]}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to fetch ratings', 'error': str(e)}), 500