import os
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.push_subscription import PushSubscription
from app.models.user import User, UserFavorite
from app.models.route import Route
from app.models.trip import Trip
from app.models.bus import Bus
from app.models.alert import UserNotification
from app.models.stop_reminder import StopReminder  # Add this import
from app.models.rating import Rating  # Add this import
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch profile', 'error': str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()

    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']

    db.session.commit()
    return jsonify({'user': user.to_dict()}), 200


@users_bp.route('/favorites', methods=['GET'])
@jwt_required()
def get_favorites():
    try:
        user_id = get_jwt_identity()
        favorites = UserFavorite.query.filter_by(user_id=user_id).all()

        favorite_routes = []
        for fav in favorites:
            route = Route.query.get(fav.route_id)
            if route:
                favorite_routes.append(route.to_dict())

        return jsonify({
            'favorites': favorite_routes
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch favorites', 'error': str(e)}), 500


@users_bp.route('/favorites/<int:route_id>', methods=['POST'])
@jwt_required()
def add_favorite(route_id):
    try:
        user_id = get_jwt_identity()

        route = Route.query.get(route_id)
        if not route:
            return jsonify({'message': 'Route not found'}), 404

        existing_favorite = UserFavorite.query.filter_by(user_id=user_id, route_id=route_id).first()
        if existing_favorite:
            return jsonify({'message': 'Route already in favorites'}), 400

        favorite = UserFavorite(user_id=user_id, route_id=route_id)
        db.session.add(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Route added to favorites',
            'favorite': favorite.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to add favorite', 'error': str(e)}), 500


@users_bp.route('/favorites/<int:route_id>', methods=['DELETE'])
@jwt_required()
def remove_favorite(route_id):
    try:
        user_id = get_jwt_identity()

        favorite = UserFavorite.query.filter_by(user_id=user_id, route_id=route_id).first()
        if not favorite:
            return jsonify({'message': 'Favorite not found'}), 404

        db.session.delete(favorite)
        db.session.commit()

        return jsonify({
            'message': 'Route removed from favorites'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to remove favorite', 'error': str(e)}), 500


@users_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        notifications = UserNotification.query.filter_by(user_id=user_id) \
            .order_by(UserNotification.created_at.desc()) \
            .paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch notifications', 'error': str(e)}), 500


@users_bp.route('/notifications/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        user_id = get_jwt_identity()
        count = NotificationService.get_unread_notifications_count(user_id)

        return jsonify({
            'unread_count': count
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch unread count', 'error': str(e)}), 500


@users_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id):
    try:
        user_id = get_jwt_identity()

        success = NotificationService.mark_notification_as_read(notification_id, user_id)
        if not success:
            return jsonify({'message': 'Notification not found'}), 404

        return jsonify({
            'message': 'Notification marked as read'
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to mark notification as read', 'error': str(e)}), 500


@users_bp.route('/notifications/read-all', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    try:
        user_id = get_jwt_identity()

        NotificationService.mark_all_notifications_as_read(user_id)

        return jsonify({
            'message': 'All notifications marked as read'
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to mark notifications as read', 'error': str(e)}), 500


@users_bp.route('/account', methods=['DELETE'])
@jwt_required()
def delete_account():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'message': 'User not found'}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': 'Account deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete account', 'error': str(e)}), 500


@users_bp.route('/avatar', methods=['POST'])
@jwt_required()
def upload_avatar():
    user_id = get_jwt_identity()

    if 'avatar' not in request.files:
        return jsonify({'message': 'No file provided'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'message': 'No file selected'}), 400

    allowed_types = {'image/jpeg', 'image/png', 'image/jpg', 'image/webp'}
    if file.mimetype not in allowed_types:
        return jsonify({'message': 'Invalid file type. Use JPEG, PNG, or WebP.'}), 400

    ext = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"avatar_{user_id}_{datetime.utcnow().timestamp()}.{ext}"

    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(upload_path)

    avatar_url = f"/uploads/{filename}"

    user = User.query.get(user_id)
    user.avatar_url = avatar_url
    db.session.commit()

    return jsonify({'avatar_url': avatar_url}), 200


# ===== STOP REMINDERS ENDPOINTS =====

@users_bp.route('/stop-reminders', methods=['GET'])
@jwt_required()
def get_stop_reminders():
    """Get all active stop reminders for the current user"""
    try:
        user_id = get_jwt_identity()

        reminders = StopReminder.query.filter_by(
            user_id=user_id,
            active=True
        ).order_by(StopReminder.created_at.desc()).all()

        return jsonify({
            'reminders': [reminder.to_dict() for reminder in reminders]
        }), 200

    except Exception as e:
        print(f"Error in get_stop_reminders: {str(e)}")
        return jsonify({'message': 'Failed to fetch reminders', 'error': str(e)}), 500


@users_bp.route('/stop-reminders', methods=['POST'])
@jwt_required()
def create_stop_reminder():
    """Create a new stop reminder (expires after 2 hours by default)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('stop_id') or not data.get('route_id'):
            return jsonify({'message': 'stop_id and route_id are required'}), 400

        # Check if reminder already exists and is active
        existing = StopReminder.query.filter_by(
            user_id=user_id,
            stop_id=data['stop_id'],
            route_id=data['route_id'],
            active=True
        ).first()

        if existing:
            return jsonify({'message': 'Reminder already exists for this stop'}), 400

        # Create reminder (expires in 2 hours by default)
        expires_at = datetime.utcnow() + timedelta(hours=2)

        reminder = StopReminder(
            user_id=user_id,
            stop_id=data['stop_id'],
            route_id=data['route_id'],
            active=True,
            expires_at=expires_at
        )

        db.session.add(reminder)
        db.session.commit()

        return jsonify({
            'message': f'Reminder set successfully',
            'reminder': reminder.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Error in create_stop_reminder: {str(e)}")
        return jsonify({'message': 'Failed to set reminder', 'error': str(e)}), 500


@users_bp.route('/stop-reminders/<int:reminder_id>', methods=['DELETE'])
@jwt_required()
def delete_stop_reminder(reminder_id):
    """Delete a stop reminder"""
    try:
        user_id = get_jwt_identity()

        reminder = StopReminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()

        if not reminder:
            return jsonify({'message': 'Reminder not found'}), 404

        db.session.delete(reminder)
        db.session.commit()

        return jsonify({'message': 'Reminder deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error in delete_stop_reminder: {str(e)}")
        return jsonify({'message': 'Failed to delete reminder', 'error': str(e)}), 500


@users_bp.route('/stop-reminders/<int:reminder_id>/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_stop_reminder(reminder_id):
    """Deactivate a reminder (soft delete)"""
    try:
        user_id = get_jwt_identity()

        reminder = StopReminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()

        if not reminder:
            return jsonify({'message': 'Reminder not found'}), 404

        reminder.active = False
        db.session.commit()

        return jsonify({'message': 'Reminder deactivated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error in deactivate_stop_reminder: {str(e)}")
        return jsonify({'message': 'Failed to deactivate reminder', 'error': str(e)}), 500


@users_bp.route('/trips', methods=['GET'])
@jwt_required()
def get_user_trips():
    try:
        user_id = get_jwt_identity()

        trips = Trip.query.filter_by(user_id=user_id) \
            .order_by(Trip.started_at.desc()).all()

        trips_data = []
        for trip in trips:
            trip_dict = trip.to_dict()

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
        return jsonify({'message': 'Failed to fetch trips', 'error': str(e)}), 500


@users_bp.route('/notifications/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_push():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('endpoint'):
            return jsonify({'message': 'Endpoint is required'}), 400

        # Check if subscription already exists
        existing = PushSubscription.query.filter_by(
            user_id=user_id,
            endpoint=data['endpoint']
        ).first()

        if existing:
            # Update existing subscription
            existing.p256dh = data.get('keys', {}).get('p256dh')
            existing.auth = data.get('keys', {}).get('auth')
            existing.updated_at = datetime.utcnow()
        else:
            # Create new subscription
            subscription = PushSubscription(
                user_id=user_id,
                endpoint=data['endpoint'],
                p256dh=data.get('keys', {}).get('p256dh'),
                auth=data.get('keys', {}).get('auth')
            )
            db.session.add(subscription)

        db.session.commit()
        return jsonify({'message': 'Subscribed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error subscribing to push: {e}")
        return jsonify({'message': 'Failed to subscribe', 'error': str(e)}), 500


@users_bp.route('/notifications/unsubscribe', methods=['DELETE'])
@jwt_required()
def unsubscribe_from_push():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data.get('endpoint'):
            return jsonify({'message': 'Endpoint is required'}), 400

        subscription = PushSubscription.query.filter_by(
            user_id=user_id,
            endpoint=data['endpoint']
        ).first()

        if subscription:
            db.session.delete(subscription)
            db.session.commit()

        return jsonify({'message': 'Unsubscribed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error unsubscribing from push: {e}")
        return jsonify({'message': 'Failed to unsubscribe', 'error': str(e)}), 500