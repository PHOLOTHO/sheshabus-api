from time import sleep
from flask import Blueprint, request, jsonify
from app import db, socketio
from app.models.bus import BusLocation
from datetime import datetime
from sqlalchemy import update

realtime_bp = Blueprint('realtime', __name__)


@realtime_bp.route('/bus-location', methods=['POST'])
def update_bus_location():
    data = request.get_json()

    for attempt in range(3):  # Retry up to 3 times
        try:
            required_fields = ['bus_id', 'device_id', 'latitude', 'longitude']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'message': f'{field} is required'}), 400

            from app.models.bus import Bus
            bus = Bus.query.filter_by(
                id=data['bus_id'],
                gps_device_id=data['device_id']
            ).first()

            if not bus:
                return jsonify({'message': 'Invalid bus or device ID'}), 400

            # Create location record
            location = BusLocation(
                bus_id=data['bus_id'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                speed=data.get('speed', 0),
                timestamp=datetime.utcnow()
            )
            db.session.add(location)

            # Update bus location using a direct UPDATE without SELECT first
            db.session.execute(
                update(Bus)
                .where(Bus.id == data['bus_id'])
                .values(
                    current_lat=data['latitude'],
                    current_lng=data['longitude'],
                    speed=data.get('speed', 0),
                    updated_at=datetime.utcnow()
                )
            )

            db.session.commit()

            print(f"📍 Bus {data['bus_id']} location updated: {data['latitude']}, {data['longitude']}")
            return jsonify({'message': 'Location updated successfully'}), 201

        except Exception as e:
            db.session.rollback()
            if "Record has changed" in str(e) or "Deadlock" in str(e):
                if attempt < 2:
                    print(f"Database conflict, retrying... (attempt {attempt + 2}/3)")
                    sleep(0.2 * (attempt + 1))
                    continue
            print(f"Error updating bus location: {e}")
            return jsonify({'message': 'Failed to update location', 'error': str(e)}), 500

    return jsonify({'message': 'Failed after retries', 'error': 'Database conflict'}), 500


@realtime_bp.route('/heartbeat', methods=['POST'])
def bus_heartbeat():
    """Receive heartbeat from Raspberry Pi"""
    try:
        data = request.get_json()

        if not data or 'bus_id' not in data:
            return jsonify({'message': 'bus_id is required'}), 400

        from app.models.bus import Bus
        bus = Bus.query.get(data['bus_id'])

        if bus:
            bus.updated_at = datetime.utcnow()
            db.session.commit()
            print(f"💓 Heartbeat from Bus {data['bus_id']} - GPS: {data.get('gps_status', 'unknown')}")

        return jsonify({'message': 'Heartbeat received'}), 200

    except Exception as e:
        print(f"Heartbeat error: {e}")
        return jsonify({'message': 'Failed to process heartbeat', 'error': str(e)}), 500


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('subscribe_to_bus')
def handle_subscribe(data):
    bus_id = data.get('bus_id')
    if bus_id:
        socketio.join_room(f'bus_{bus_id}')
        print(f'Client subscribed to bus {bus_id}')


@socketio.on('unsubscribe_from_bus')
def handle_unsubscribe(data):
    bus_id = data.get('bus_id')
    if bus_id:
        socketio.leave_room(f'bus_{bus_id}')
        print(f'Client unsubscribed from bus {bus_id}')