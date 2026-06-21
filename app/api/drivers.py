from flask import Blueprint, request, jsonify
from app import db
from app.models.driver import Driver

drivers_bp = Blueprint('drivers', __name__)


@drivers_bp.route('/', methods=['GET'])
def get_drivers():
    try:
        status = request.args.get('status', 'active')

        drivers = Driver.query.filter_by(status=status).all()

        return jsonify({
            'drivers': [driver.to_dict() for driver in drivers]
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch drivers', 'error': str(e)}), 500


@drivers_bp.route('/<int:driver_id>', methods=['GET'])
def get_driver(driver_id):
    try:
        driver = Driver.query.get_or_404(driver_id)

        return jsonify({
            'driver': driver.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch driver', 'error': str(e)}), 500