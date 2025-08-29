from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt, get_jwt_identity,
                                set_refresh_cookies, set_access_cookies)
import redis
from datetime import datetime
from app.models.v1 import User, Department, Role
from app.extensions import db, bcrypt, jwt
from marshmallow import ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.validations.auth_validate import (
    RegUserSchema,
    LoginSchema, UpdateUserSchema)


auth_bp = Blueprint("auth", __name__)
BLACKLIST_PREFIX = "jwt_blacklist_"

limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

redis_client = redis.Redis(
                host='172.26.137.76',
                port=6379,
                password='qwerty254',
                decode_responses=True
        )


@auth_bp.route('/auth/register', methods=['POST'])
def create_user():
    """create new user"""
    try:
        if not request.is_json:
            return jsonify({
                "error": "Unsupported Media Type. \
                Content-Type must be application/json."}), 415
        user_data = request.get_json()
        user_info = RegUserSchema().load(user_data)
        new_user = User(
            email=user_info['email'],
            password=user_info['password'],
            fullname=user_info['fullname'],
            department_id=user_info['department_id'],
            role_id=user_info['role_id']
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "message": "User registered successfully!",
            "user": {
                "name": new_user.fullname,
                "email": new_user.email,
                "department_id": new_user.department_id,
                "role_id": new_user.role_id
            }
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@auth_bp.route('/auth/login', methods=['POST'], strict_slashes=False)
def login():
    try:
        if not request.is_json:
            return jsonify({
                "error": "Unsupported Media Type. \
                    Content-Type must be application/json."
            }), 415

        user_data = request.get_json()
        user_info = LoginSchema().load(user_data)

        email = user_info.get('email')
        password = user_info.get('password')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))

            response = jsonify({
                "user": {
                    "fullname": user.fullname,
                    "email": user.email,
                    "department_id": user.department_id,
                    "role_id": user.role_id
                }
            })

            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)

            return response

        return jsonify({"message": "Invalid email or password"}), 401

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    "logout a user by disabling access token"
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    exp_timestamp = get_jwt()["exp"]
    now = int(datetime.utcnow().timestamp())
    ttl = exp_timestamp - now
    redis_client.setex(f"{BLACKLIST_PREFIX}{token_type}_{jti}", ttl, 1)
    redis_client.setex(f"{BLACKLIST_PREFIX}refresh_{jti}", ttl, 1)
    return jsonify({"msg": "Successfully logged out"}), 200


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_type = jwt_payload.get("type", "access")
    return redis_client.exists(f"{BLACKLIST_PREFIX}{token_type}_{jti}") > 0

@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Invalid user"}), 401
    department = db.session.get(Department, user.department_id) \
            if user.department_id else None
    role = db.session.get(Role, user.role_id) if user.role_id else None
    if department:
        department_name = department.name
    else:
        department_name = "Unknown Department"
    role_name = role.name if role else "Unknown Role"

    return jsonify({
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "department": department_name,
        "role": role_name
    }), 200


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        jti = get_jwt()["jti"]
        if redis_client.exists(f"{BLACKLIST_PREFIX}refresh_{jti}"):
            return jsonify({"error": "Token has been revoked"}), 401

        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id)

        user = User.query.get(current_user_id)
        if not user:
            return jsonify({"error": "Invalid user"}), 404

        department = db.session.get(Department, user.department_id) \
            if user.department_id else None
        role = db.session.get(Role, user.role_id) if user.role_id else None

        response = jsonify({
            "msg": "Token refreshed successfully",
            "user": {
                "fullname": user.fullname,
                "email": user.email,
                "department_id": department.name if department else None,
                "role_id": role.name if role else None
            }
        })

        set_access_cookies(response, new_access_token)
        return response, 200

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@auth_bp.route('/auth/update/<user_id>', methods=['PUT'])
@jwt_required()
def Update_User_Info(user_id):
    """Update user info in the database"""
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                " Content-Type must be application/json."
            }), 415
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                "error":
                f"User with id {user_id} not found."
            }), 404
        user_data = request.get_json()
        user_info = UpdateUserSchema().load(user_data)
        if 'username' in user_data:
            user.fullname = user_info['fullname']
        if 'email' in user_data:
            user.email = user_info['email']
        if 'role_id' in user_data:
            user.role_id = user_info['role_id']
        if 'department_id' in user_data:
            user.department_id = user_info['department_id']
        db.session.commit()
        department = Department.query.get(user.department_id)
        role = Role.query.get(user.role_id)
        if department:
            department_name = department.name
        else:
            department_name = "Unknown Department"
        role_name = role.name if role else "Unknown Role"
        return jsonify({"Success": "User Updated",
                        "Details": {
                            "role_id": role_name,
                            "email": user.email,
                            "fullname": user.fullname,
                            "department_id": department_name
                        }}), 200

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@auth_bp.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Retrieve user details by user ID.
    This endpoint fetches user information (ID, full name, and department)
        from the database.
    Requires a valid JWT token.
    Args:
        user_id (str): The ID of the user to fetch.
    Returns:
        JSON response with user details (200) or error message (404/500).
    """
    try:
        if not isinstance(user_id, int):
            return jsonify({"error": "Invalid user ID format."}), 400
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return jsonify({"Error": f"User with id {user_id} not found"}), 404
        department = db.session.get(Department, user.department_id) \
            if user.department_id else None
        role = db.session.get(Role, user.role_id) if user.role_id else None
        if department:
            department_name = department.name
        else:
            department_name = "Unknown Department"
        role_name = role.name if role else "Unknown Role"
        return jsonify({
            "user": {
                "fullname": user.fullname,
                "email": user.email,
                "department": department_name,
                "role": role_name
            }
        }), 200
    except ValueError:
        return jsonify({
            "error": "user id must be an integer"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """
    Retrieve all user details.
    This endpoint fetches all users along with their department and role.
    Requires a valid JWT token.
    Returns:
        JSON response with list of users (200) or error message (500).
    """
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            department = db.session.get(
                Department, user.department_id) if user.department_id else None
            role = db.session.get(Role, user.role_id) if user.role_id else None
            user_list.append({
                "id": user.id,
                "fullname": user.fullname,
                "email": user.email,
                "department": department.name if department else \
                    "Unknown Department",
                "role": role.name if role else "Unknown Role"
            })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
