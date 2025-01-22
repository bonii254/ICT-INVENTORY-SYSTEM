from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Status
from flask_jwt_extended import jwt_required
from utils.validations.status_validate import RegStatusSchema

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
        status_data = request.get_json()
        status_info = RegStatusSchema().load(status_data)
        new_status = Status(
            name=status_info["name"],
            description=status_info["description"]
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
