from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.route import Route, RouteStop, Stop
from app.models.bus import BusAssignment
from app.models.schedule import Schedule
from app.services.location_service import LocationService
from datetime import date

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('', methods=['GET'])
@routes_bp.route('/', methods=['GET'])
def get_routes():
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        query = Route.query
        if active_only:
            query = query.filter_by(is_active=True)

        routes = query.all()

        routes_data = []
        for route in routes:
            routes_data.append({
                'id': str(route.id),
                'name': route.name,
                'number': route.number,
                'color': route.color,
                'fare': float(route.fare) if route.fare else 0,
                'start_point': route.start_point,
                'end_point': route.end_point
            })

        return jsonify({'routes': routes_data}), 200

    except Exception as e:
        print(f"Error in get_routes: {str(e)}")
        return jsonify({'message': 'Failed to fetch routes', 'error': str(e)}), 500


@routes_bp.route('/nearby', methods=['GET'])
@jwt_required()
def get_nearby_routes():
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 5, type=float)

        if not lat or not lng:
            return jsonify({'message': 'Latitude and longitude are required'}), 400

        routes = Route.query.filter_by(is_active=True).all()
        nearby_routes = []

        for route in routes:
            for stop in route.stops:
                distance = LocationService.calculate_distance(
                    lat, lng, stop.lat, stop.lng
                )
                if distance <= radius:
                    nearby_routes.append(route)
                    break

        return jsonify({
            'routes': [route.to_dict() for route in nearby_routes]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch nearby routes', 'error': str(e)}), 500


@routes_bp.route('/<int:route_id>', methods=['GET'])
def get_route(route_id):
    detailed = request.args.get('detailed', 'false').lower() == 'true'
    route = Route.query.get_or_404(route_id)
    return jsonify({'route': route.to_dict(detailed=detailed)}), 200


@routes_bp.route('/<int:route_id>/buses', methods=['GET'])
def get_route_buses(route_id):
    try:
        route = Route.query.get_or_404(route_id)

        active_assignments = BusAssignment.query.filter_by(
            route_id=route_id,
            is_active=True,
            assignment_date=date.today()
        ).all()

        buses = []
        for assignment in active_assignments:
            bus_data = assignment.bus.to_dict()
            latest_location = assignment.bus.locations.order_by(db.desc('timestamp')).first()
            if latest_location:
                bus_data['current_location'] = latest_location.to_dict()
            bus_data['driver'] = assignment.driver.to_dict() if assignment.driver else None
            buses.append(bus_data)

        return jsonify({'buses': buses}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch route buses', 'error': str(e)}), 500


@routes_bp.route('/<int:route_id>/stops', methods=['GET'])
def get_route_stops(route_id):
    try:
        route_stops = db.session.query(RouteStop, Stop).join(
            Stop, RouteStop.stop_id == Stop.id
        ).filter(RouteStop.route_id == route_id).order_by(RouteStop.sequence).all()

        stops_data = []
        for rs, stop in route_stops:
            stop_dict = stop.to_dict()
            stop_dict['sequence'] = rs.sequence
            stop_dict['scheduled_time'] = rs.scheduled_time.isoformat() if rs.scheduled_time else None
            stops_data.append(stop_dict)

        return jsonify({'stops': stops_data}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch route stops', 'error': str(e)}), 500


@routes_bp.route('/<int:route_id>/schedules', methods=['GET'])
def get_route_schedules(route_id):
    try:
        schedules = Schedule.query.filter_by(route_id=route_id).all()

        schedules_data = []
        for schedule in schedules:
            schedules_data.append({
                'id': schedule.id,
                'route_id': schedule.route_id,
                'day_type': schedule.day_type,
                'first_bus': schedule.first_bus.isoformat() if schedule.first_bus else None,
                'last_bus': schedule.last_bus.isoformat() if schedule.last_bus else None,
                'frequency_minutes': schedule.frequency_minutes
            })

        return jsonify({'schedules': schedules_data}), 200

    except Exception as e:
        print(f"Error in get_route_schedules: {str(e)}")
        return jsonify({'message': 'Failed to fetch schedules', 'error': str(e)}), 500


@routes_bp.route('/stops', methods=['GET'])
def get_all_stops():
    try:
        stops = Stop.query.all()
        stops_data = []
        for stop in stops:
            stops_data.append({
                'id': str(stop.id),
                'name': stop.name,
                'lat': float(stop.lat),
                'lng': float(stop.lng),
                'is_accessible': stop.is_accessible,
                'landmarks': stop.landmarks
            })
        return jsonify({'stops': stops_data}), 200
    except Exception as e:
        print(f"Error in get_all_stops: {str(e)}")
        return jsonify({'stops': []}), 200