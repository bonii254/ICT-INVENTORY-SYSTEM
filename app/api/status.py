from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError 
from app.extensions import db
from app.models.v1 import Status
from flask_jwt_extended import jwt_required 
from utils.validations.status_validate import (
    RegStatusSchema, UpdatestatusSchema)

status_bp = Blueprint("status_bp", __name__)


@status_bp.route("/register/status", methods=['POST'])
@jwt_required()
def create_status():
    """
    Create a new Status.

    This endpoint allows authenticated users to create a new Status by
    providing the `name` in the request body. Validates input using a
    schema and saves the Status to the database.

    Returns:
        - 201: Status created successfully.
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
                "Unsupported Media Type. Content-Type must be application/json"
            }), 415
        current_user = getattr(g, 'current_user', None)
        status_data = request.get_json()
        status_info = RegStatusSchema().load(status_data)
        new_status = Status(
            name=status_info["name"],
            description=status_info["description"],
            domain_id=current_user.domain_id
        )
        db.session.add(new_status)
        db.session.commit()
        return jsonify({
            "message": "Status created successfully",
            "Status": {
                "name": new_status.name,
                "description": new_status.description
            }
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
                f"an unexpected error occurred: {str(e)}"
        }), 500


@status_bp.route('/status/<int:status_id>', methods=['PUT'])
@jwt_required()
def update_status(status_id):
    """
    Update an existing status.

    This endpoint allows authenticated users to update the details of an
    existing status by providing the updated `name` and/or `description`
    in the request body.

    Returns:
        - 200: status updated successfully.
        - 400: Validation error or invalid input.
        - 404: status not found.
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
        status = Status.query.get(status_id)
        if not status:
            return jsonify({
                "error": f"Status with ID {status_id} not found."
            }), 404
        status_data = request.get_json()
        updated_data = UpdatestatusSchema().load(status_data)
        if 'name' in updated_data:
            status.name = updated_data['name'].capitalize()
        if 'description' in updated_data:
            status.description = updated_data['description']
        db.session.commit()
        return jsonify({
            "message": "Status updated successfully!",
            "status": {
                "id": status.id,
                "name": status.name,
                "description": status.description
            }
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@status_bp.route('/status/<int:status_id>', methods=['GET'])
@jwt_required()
def get_status(status_id):
    """
    Retrieve a specific status by ID.
    Args:
        status_id (int): The ID of the status to retrieve.
    Returns:
        JSON response with the status details,
        or an error message if not found.
    """
    try:
        status = Status.query.get(status_id)
        if not status:
            return jsonify({
                "error": f"Status with id {status_id} not found"
                }), 404
        return jsonify({
            "status": {
                "id:": status.id,
                "name": status.name,
                "description": status.description
            }
        })
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@status_bp.route('/statuses', methods=['GET'])
@jwt_required()
def get_all_statuses():
    """
    Retrieve all statuses.
    Returns:
        JSON response with a list of all statuses,
        or an error message if unsuccessful.
    """
    try:
        statuses = Status.query.all()
        status_list = [
            {
                "id": status.id,
                "name": status.name,
                "description": status.description
            } for status in statuses
        ]
        return jsonify(status_list), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@status_bp.route('/status/<int:status_id>', methods=['DELETE'])
@jwt_required()
def delete_status(status_id):
    """
    Delete a status by ID.
        Args:
    status_id (int): The ID of the status to delete.
    Returns:
        JSON response confirming deletion,
        or an error message if the status does not exist.
    """
    try:
        status = Status.query.get(status_id)
        if status:
            db.session.delete(status)
            db.session.commit()
            return jsonify({
                "Message": "status deleted successfully"
            }), 201
        return jsonify({
            "Error": f"status with id {status_id} does not exist"
        }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
