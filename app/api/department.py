from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Department
from flask_jwt_extended import jwt_required
from utils.validations.dep_validate import RegDepSchema, UpdateDepSchema


dep_bp = Blueprint("dep_bp", __name__)


@dep_bp.route('/register/department', methods=['POST'])
@jwt_required()
def create_department():
    """
    Create a new Department.

    This endpoint allows authenticated users to create a new department by
    providing the `name` in the request body. Validates input
    using a schema and saves the role to the database.

    Returns:
        - 201: Department created successfully.
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
                "Unsupported Media Type. Content-Type must be application/json."
            }), 415
        dep_data = request.get_json()
        dep_info = RegDepSchema().load(dep_data)
        new_dep = Department(name=dep_info["name"])
        db.session.add(new_dep)
        db.session.commit()
        return jsonify({
            "message": "Department registered successfully!",
            "Department": {
                "name": new_dep.name
            }
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@dep_bp.route('/department/<int:department_id>', methods=['PUT'])
@jwt_required()
def update_department(department_id):
    """
    Update an existing Department.

    This endpoint allows authenticated users to update the details of an
    existing department by providing the updated `name` in the request body.

    Returns:
        - 200: Department updated successfully.
        - 400: Validation error or invalid input.
        - 404: Department not found.
        - 415: Unsupported Media Type.
        - 500: Internal server error.

    Security:
        - Requires JWT authentication.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type. Content-Type must be application/json."
            }), 415
        department = Department.query.get(department_id)
        if not department:
            return jsonify({
                "error": f"Department with ID {department_id} not found."
            }), 404
        department_data = request.get_json()
        updated_data = UpdateDepSchema().load(department_data)
        if 'name' in updated_data:
            department.name = updated_data['name']
        db.session.commit()
        return jsonify({
            "message": "Department updated successfully!",
            "department": {
                "id": department.id,
                "name": department.name
            }
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

