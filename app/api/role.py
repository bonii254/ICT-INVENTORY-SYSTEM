from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Role
from flask_jwt_extended import jwt_required
from utils.validations.role_validate import RegRoleSchema, UpdateRoleSchema


role_bp = Blueprint("role_bp", __name__)


@role_bp.route('/register/role', methods=['POST'])
#@jwt_required()
def create_role():
    """
    Create a new role.

    This endpoint allows authenticated users to create a new role by providing
    the `name` and `permissions` in the request body. Validates input using a
    schema and saves the role to the database.

    Returns:
        - 201: Role created successfully.
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
        role_data = request.get_json()
        new_role = RegRoleSchema().load(role_data)
        db.session.add(new_role)
        db.session.commit()
        return jsonify({
            "message": "Role registered successfully!",
            "Role": {
                "name": new_role.name,
                "permissions": new_role.permissions
            }
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@role_bp.route('/role/<int:role_id>', methods=['PUT'])
@jwt_required()
def update_role(role_id):
    """
    Update an existing role.

    This endpoint allows authenticated users to update the details of an
    existing role by providing the updated `name` and/or `permissions`
    in the request body.

    Returns:
        - 200: Role updated successfully.
        - 400: Validation error or invalid input.
        - 404: Role not found.
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
        role = db.session.get(Role, role_id)
        if not role:
            return jsonify({
                "error": f"Role with ID {role_id} not found."
            }), 404
        role_data = request.get_json()
        updated_data = UpdateRoleSchema().load(role_data)
        if 'name' in updated_data:
            role.name = updated_data['name']
        if 'permissions' in updated_data:
            role.permissions = updated_data['permissions']
        db.session.commit()
        return jsonify({
            "message": "Role updated successfully!",
            "role": {
                "id": role.id,
                "name": role.name,
                "permissions": role.permissions
            }
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@role_bp.route('/role/<int:role_id>', methods=['GET'])
@jwt_required()
def get_role(role_id):
    """
    Retrieve a specific role by ID.
    Args:
        role_id (int): The ID of the role to retrieve.
    Returns:
        JSON response with the role details,
        or an error message if not found.
    """
    try:
        role = db.session.get(Role, role_id)
        if not role:
            return jsonify({
                "error": f"role with id {role_id} not found."
                }), 404
        return jsonify({
            "role": {
                "id:": role.id,
                "name": role.name,
                "permissions": role.permissions
            }
        })
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@role_bp.route('/roles', methods=['GET'])
@jwt_required()
def get_all_roles():
    """
    Retrieve all roles.
    Returns:
        JSON response with a list of all roles,
        or an error message if unsuccessful.
    """
    try:
        roles = Role.query.all()
        role_list = [
            {
                "id": role.id,
                "name": role.name,
                "permissions": role.permissions
            } for role in roles
        ]
        return jsonify(role_list), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@role_bp.route('/role/<int:role_id>', methods=['DELETE'])
@jwt_required()
def delete_role(role_id):
    """
    Delete a role by ID.
        Args:
    role_id (int): The ID of the role to delete.
    Returns:
        JSON response confirming deletion,
        or an error message if the role does not exist.
    """
    try:
        role = db.session.get(Role, role_id)
        if role:
            db.session.delete(role)
            db.session.commit()
            return jsonify({
                "Message": "role deleted successfully"
            }), 200
        return jsonify({
            "Error": f"role with id {role_id} does not exist"
        }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
