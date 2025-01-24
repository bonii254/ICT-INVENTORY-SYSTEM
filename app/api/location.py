from flask import jsonify, Blueprint, request
from app.models.v1 import Location
from app.extensions import db
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from utils.validations.loc_validate import RegLocSchema


loc_bp = Blueprint("loc_bp", __name__)


@loc_bp.route('/register/location', methods=['POST'])
@jwt_required()
def create_location():
    """"
    Register a new location.

    This endpoint allows authenticated users to register a new location by
    providing `name` and `address` in the request body. Validates input using
    a schema and saves the location to the database.

    Returns:
        - 201: Location created successfully.
        - 400: Validation error.
        - 415: Unsupported Media Type.
        - 500: Internal server error.

    Security:
        - Requires JWT authentication.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        location_data = request.get_json()
        location_info = RegLocSchema().load(location_data)
        new_location = Location(
            name=location_info["name"],
            address=location_info["address"],
        )
        db.session.add(new_location)
        db.session.commit()
        return jsonify({
            "message": "Location registered successfully!",
            "Location": {
                "name": new_location.name,
                "address": new_location.address
            }
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500
