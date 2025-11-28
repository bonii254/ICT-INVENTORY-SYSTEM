from flask import jsonify, Blueprint, request, g
from app.models.v1 import Location
from app.extensions import db
from flask_jwt_extended import jwt_required 
from marshmallow import ValidationError 
from utils.validations.loc_validate import RegLocSchema, UpdateLocSchema


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
        current_user = getattr(g, "current_user", None)
        if not current_user:
            return jsonify({"error": "Unauthorized"})
        location_data = request.get_json()
        location_info = RegLocSchema().load(location_data)
        new_location = Location(
            name=location_info["name"],
            address=location_info["address"],
            domain_id=current_user.domain_id
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


@loc_bp.route('/location/<int:location_id>', methods=['PUT'])
@jwt_required()
def update_location(location_id):
    """
    Update a location's details by ID.
    Args:
        location_id (int): The ID of the location to update.
    Returns:
        JSON response with the updated location details,
        or an error message if unsuccessful.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        location = db.session.get(Location, location_id)
        if not location:
            return jsonify({
                "error": f"location with ID {location_id} not found."
            }), 404
        location_data = request.get_json()
        validated_location = UpdateLocSchema().load(location_data)
        if 'name' in validated_location:
            location.name = validated_location['name']
        if 'address' in validated_location:
            location.address = validated_location['address']
        db.session.commit()
        return jsonify({
            "Message": "Location updated successfully",
            "location": {
                "id:": location.id,
                "name": location.name,
                "address": location.address
            }
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@loc_bp.route('/location/<int:location_id>', methods=['GET'])
@jwt_required()
def get_location(location_id):
    """
    Retrieve a specific location by ID.
    Args:
        location_id (int): The ID of the location to retrieve.
    Returns:
        JSON response with the location details,
        or an error message if not found.
    """
    try:
        location = db.session.get(Location, location_id)
        if not location:
            return jsonify({
                "error": f"Location with id {location_id} not found"
                }), 404
        return jsonify({
            "location": {
                "id:": location.id,
                "name": location.name,
                "address": location.address
            }
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@loc_bp.route('/locations', methods=['GET'])
@jwt_required()
def get_all_locations():
    """
    Retrieve all locations.
    Returns:
        JSON response with a list of all locations,
        or an error message if unsuccessful.
    """
    try:
        locations = Location.query.all()
        location_list = [
            {
                "id": location.id,
                "name": location.name,
                "address": location.address
            } for location in locations
        ]
        return jsonify(location_list), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@loc_bp.route('/location/<int:location_id>', methods=['DELETE'])
@jwt_required()
def delete_location(location_id):
    """
    Delete a location by ID.
        Args:
    location_id (int): The ID of the location to delete.
    Returns:
        JSON response confirming deletion,
        or an error message if the location does not exist.
    """
    try:
        location = db.session.get(Location, location_id)
        if location:
            db.session.delete(location)
            db.session.commit()
            return jsonify({
                "Message": "Location deleted successfully"
            }), 200
        return jsonify({
            "Error": f"Location with id {location_id} does not exist"
        }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
