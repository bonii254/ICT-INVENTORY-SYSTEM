from flask import Blueprint, request, jsonify, current_app as app
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt, get_jwt_identity,)
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
                host='172.21.142.162',
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
#@limiter.limit("10 per minute")
def login():
    """login a user by authentification"""
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                " Content-Type must be application/json."
            }), 415
        user_data = request.get_json()
        user_info = LoginSchema().load(user_data)
        email = user_info.get('email')
        password = user_info.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(identity=str(user.id))
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "fullname": user.fullname,
                    "email": user.email,
                    "department_id": user.department_id,
                    "role_id": user.role_id
                }
            }), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    "logout a user by disabling access token"
    jti = get_jwt()["jti"]
    token_type = get_jwt()["type"]
    exp_timestamp = get_jwt()["exp"]
    now = int(datetime.utcnow().timestamp())
    ttl = exp_timestamp - now
    redis_client.setex(f"{BLACKLIST_PREFIX}{token_type}_{jti}", ttl, "true")
    return jsonify({"msg": "Successfully logged out"}), 200


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_type = jwt_payload["type"]
    return redis_client.exists(f"{BLACKLIST_PREFIX}{token_type}_{jti}") > 0


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using the refresh token"""
    try:
        current_user = str(get_jwt_identity())
        new_access_token = create_access_token(identity=current_user)
        return jsonify({
            "access_token": new_access_token
        }), 200
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
        if not user_id.isdigit():
            return jsonify({"Error": "Invalid user ID format"}), 400
        user = User.query.filter_by(id=user_id).first()
        if user:
            department = Department.query.get(user.department_id)
            role = Role.query.get(user.role_id)
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
        return jsonify({"Error": f"User with id {user_id} not found"}), 404
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
