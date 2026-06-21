from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.alert import Alert, UserAlert
from app.services.notification_service import NotificationService
from datetime import datetime, timedelta

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('/', methods=['GET'])
def get_alerts():
    try:
        alert_type = request.args.get('type')
        priority = request.args.get('priority')
        sent_only = request.args.get('sent_only', 'false').lower() == 'true'

        query = Alert.query

        if alert_type:
            query = query.filter_by(alert_type=alert_type)
        if priority:
            query = query.filter_by(priority=priority)
        if sent_only:
            query = query.filter_by(is_sent=True)

        alerts = query.order_by(Alert.created_at.desc()).all()

        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch alerts', 'error': str(e)}), 500


@alerts_bp.route('/active', methods=['GET'])
@jwt_required(optional=True)
def get_active_alerts():
    try:
        # Simple query - don't join with user_alerts for now
        alerts = Alert.query.filter(
            Alert.is_sent == True,
            Alert.expires_at > datetime.utcnow()
        ).order_by(Alert.created_at.desc()).limit(20).all()

        result = []
        for alert in alerts:
            result.append({
                'id': alert.id,
                'type': alert.type,
                'title': alert.title,
                'body': alert.body,
                'route_id': alert.route_id,
                'priority': alert.priority,
                'created_at': alert.created_at.isoformat() if alert.created_at else None,
                'expires_at': alert.expires_at.isoformat() if alert.expires_at else None
            })

        return jsonify({'alerts': result}), 200

    except Exception as e:
        print(f"Error in get_active_alerts: {str(e)}")
        # Return empty array instead of error
        return jsonify({'alerts': [], 'message': str(e)}), 200


@alerts_bp.route('/', methods=['POST'])
@jwt_required()
def create_alert():
    try:
        current_user = get_jwt_identity()
        if not current_user.startswith('admin_'):
            return jsonify({'message': 'Admin access required'}), 403

        data = request.get_json()

        required_fields = ['title', 'message', 'alert_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} is required'}), 400

        alert = Alert(
            title=data['title'],
            body=data['message'],  # was 'message'
            type=data['alert_type'],  # was 'alert_type'
            priority=data.get('priority', 'medium'),
            route_id=data.get('target_route_id'),  # was 'target_route_id'
            bus_id=data.get('target_bus_id'),  # was 'target_bus_id'
            # send_to_all is removed – targeting now based on route_id/bus_id
            sent_by=int(current_user.replace('admin_', '')),
            scheduled_for=data.get('scheduled_for')
        )

        db.session.add(alert)
        db.session.commit()

        # If no scheduled time, send immediately
        if not alert.scheduled_for:
            NotificationService.send_alert_to_users(alert)

        return jsonify({
            'message': 'Alert created successfully',
            'alert': alert.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create alert', 'error': str(e)}), 500


@alerts_bp.route('/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    try:
        alert = Alert.query.get_or_404(alert_id)

        return jsonify({
            'alert': alert.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch alert', 'error': str(e)}), 500


@alerts_bp.route('/<int:alert_id>/send', methods=['POST'])
@jwt_required()
def send_alert(alert_id):
    try:
        current_user = get_jwt_identity()
        if not current_user.startswith('admin_'):
            return jsonify({'message': 'Admin access required'}), 403

        alert = Alert.query.get_or_404(alert_id)

        if alert.is_sent:
            return jsonify({'message': 'Alert already sent'}), 400

        notifications_sent = NotificationService.send_alert_to_users(alert)

        return jsonify({
            'message': f'Alert sent to {notifications_sent} users',
            'alert': alert.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to send alert', 'error': str(e)}), 500


@alerts_bp.route('/<int:alert_id>/read', methods=['PUT'])
@jwt_required()
def mark_alert_read(alert_id):
    user_id = get_jwt_identity()

    user_alert = UserAlert.query.filter_by(
        user_id=user_id, alert_id=alert_id
    ).first()

    if not user_alert:
        user_alert = UserAlert(user_id=user_id, alert_id=alert_id)
        db.session.add(user_alert)

    user_alert.read_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Alert marked as read'}), 200