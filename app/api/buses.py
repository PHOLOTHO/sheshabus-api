from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.bus import Bus, BusLocation
from datetime import datetime, timedelta

buses_bp = Blueprint('buses', __name__)


@buses_bp.route('', methods=['GET'])  # Add this
@buses_bp.route('/', methods=['GET'])
def get_buses():
    try:
        route_id = request.args.get('route_id', type=int)

        query = Bus.query
        if route_id:
            query = query.filter_by(route_id=route_id)

        buses = query.all()
        return jsonify({'buses': [bus.to_dict() for bus in buses]}), 200
    except Exception as e:
        print(f"Error in get_buses: {str(e)}")
        return jsonify({'message': 'Failed to fetch buses', 'error': str(e)}), 500


@buses_bp.route('/<int:bus_id>', methods=['GET'])
def get_bus(bus_id):
    try:
        bus = Bus.query.get_or_404(bus_id)

        return jsonify({
            'bus': bus.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch bus', 'error': str(e)}), 500


@buses_bp.route('/<int:bus_id>/location', methods=['GET'])
def get_bus_location(bus_id):
    try:
        bus = Bus.query.get_or_404(bus_id)

        # Get latest location
        location = bus.locations.order_by(db.desc('timestamp')).first()

        if not location:
            return jsonify({'message': 'No location data available'}), 404

        return jsonify({
            'location': location.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch bus location', 'error': str(e)}), 500


@buses_bp.route('/<int:bus_id>/location-history', methods=['GET'])
def get_bus_location_history(bus_id):
    try:
        bus = Bus.query.get_or_404(bus_id)
        hours = request.args.get('hours', 1, type=int)

        since_time = datetime.utcnow() - timedelta(hours=hours)
        locations = bus.locations.filter(BusLocation.timestamp >= since_time) \
            .order_by(BusLocation.timestamp.asc()).all()

        return jsonify({
            'locations': [location.to_dict() for location in locations]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch location history', 'error': str(e)}), 500


@buses_bp.route('/active', methods=['GET'])
def get_active_buses():
    try:
        # Get buses with locations in the last 5 minutes
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)

        active_buses = db.session.query(Bus).join(BusLocation) \
            .filter(BusLocation.timestamp >= five_minutes_ago) \
            .filter(Bus.status == 'active') \
            .distinct().all()

        buses_with_locations = []
        for bus in active_buses:
            bus_data = bus.to_dict()
            latest_location = bus.locations.order_by(db.desc('timestamp')).first()
            if latest_location:
                bus_data['current_location'] = latest_location.to_dict()
            buses_with_locations.append(bus_data)

        return jsonify({
            'buses': buses_with_locations
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch active buses', 'error': str(e)}), 500