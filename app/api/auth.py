from flask import Blueprint, request, jsonify, current_app as app, g
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, get_jwt, get_jwt_identity,
                                set_refresh_cookies, set_access_cookies,
                                unset_jwt_cookies,)
import secrets
import traceback
import string
from flask_mail import Message
from datetime import datetime, timezone
from app.models.v1 import User, Department, Role, Domain, RevokedToken
from app.extensions import db, bcrypt, jwt, mail
from marshmallow import ValidationError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.validations.auth_validate import (
    RegUserSchema,
    LoginSchema, UpdateUserSchema, UpdatePasswordSchema)
from utils.token_helpers import is_token_revoked, admin_required
from utils.email_helper import send_welcome_email, send_password_changed_email


auth_bp = Blueprint("auth", __name__)

limiter = Limiter(
    get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])


@auth_bp.route('/auth/register', methods=['POST'])
@jwt_required()
def create_user():
    """Register a new user and send password via email."""
    try:
        if not request.is_json:
            return jsonify({
                "error": 
                    "Unsupported Media Type. Content-Type must be application/json."
            }), 415
        current_user_id = get_jwt_identity()
        current_user = db.session.get(User, current_user_id)
        user_data = request.get_json()
        user_info = RegUserSchema().load(user_data)

        alphabet = string.ascii_letters + string.digits + string.punctuation
        raw_password = ''.join(secrets.choice(alphabet) for _ in range(10))
        hashed_password = bcrypt.generate_password_hash(
            raw_password).decode('UTF-8')

        new_user = User(
            email=user_info['email'],
            password=hashed_password,
            fullname=user_info['fullname'],
            department_id=user_info['department_id'],
            payroll_no=user_info['payroll_no'],
            role_id=user_info['role_id'],
            domain_id=current_user.domain_id,
            is_active=user_info.get('is_active', True),
        )

        db.session.add(new_user)
        db.session.commit()
        new_user.must_change_password = True
        new_user.password_changed_by = current_user_id
        new_user.password_changed_at = datetime.now(timezone.utc)
        db.session.commit()

        send_welcome_email(new_user.fullname, new_user.email, raw_password)


        return jsonify({
            "message": "User registered successfully! Login credentials have been sent to the user’s email.",
            "user": {
                "name": new_user.fullname,
                "email": new_user.email,
                "department_id": new_user.department_id,
                "role_id": new_user.role_id,
                "domain_id": new_user.domain_id,
                "payroll_no": new_user.payroll_no
            }
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@auth_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 415

        data = request.get_json()
        credentials = LoginSchema().load(data)

        user = User.query.filter_by(email=credentials['email']).first()

        if not user or not bcrypt.check_password_hash(
            user.password, credentials['password']):
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.is_active:
            return jsonify({"error": "Account is deactivated"}), 403

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        response = jsonify({
            "message": "Login successful",
            "user": user.to_dict(),
        })
        set_access_cookies(response, access_token)
        set_refresh_cookies(response, refresh_token)
        
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        return response, 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()
        return jsonify({"error": "Internal server error"}), 500

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return is_token_revoked(jwt_payload)


@auth_bp.route('/auth/admin/reset-password/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_reset_password(user_id):
    """
    Admin resets another user's password.
    Body (optional): {"new_password": "StrongPass#123"} — if omitted, 
    random password is generated.
    Sets must_change_password = True.
    """
    if not request.is_json:
        return jsonify({
            "error": "Content-Type must be application/json."}), 415

    try:
        caller = db.session.get(User, get_jwt_identity())
        target = db.session.get(User, user_id)
        if not target:
            return jsonify({"error": "Target user not found."}), 404

        body = request.get_json() or {}
        new_password = body.get("new_password")
        if new_password:
            pass
        else:
            alphabet = string.ascii_letters + string.digits + string.punctuation
            new_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        target.password = bcrypt.generate_password_hash(
            new_password).decode('utf-8')
        target.must_change_password = True
        target.password_changed_by = caller.id
        target.password_changed_at = datetime.now(timezone.utc)
        db.session.commit()

        try:
            send_password_changed_email(
                target.fullname, target.email, new_password)
        except Exception:
            app.logger.exception("Failed to send admin-reset email (non-fatal)")

        return jsonify({
            "message": "Password reset. User will be required to change it on next login.",
        }), 200

    except Exception as e:
        db.session.rollback()
        app.logger.exception(e)
        return jsonify({"error": "Unexpected server error"}), 500
    
    
@auth_bp.route('/auth/update-password', methods=['PUT'])
@jwt_required()
def update_password():
    """Owner updates their own password. Clears must_change_password."""
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json."}), 415

    try:
        data = request.get_json()
        validated_data = UpdatePasswordSchema().load(data)

        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        if not bcrypt.check_password_hash(user.password, validated_data["current_password"]):
            return jsonify({"error": "Current password is incorrect."}), 401

        user.password = bcrypt.generate_password_hash(validated_data["new_password"]).decode('utf-8')
        user.must_change_password = False
        user.password_changed_by = user.id
        user.password_changed_at = datetime.now(timezone.utc)
        db.session.commit()

        return jsonify({"message": "Password updated successfully."}), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        print("Exception occurred:")
        traceback.print_exc()
        app.logger.exception(e)
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)

        response = jsonify({"message": "Access token refreshed"})
        set_access_cookies(response, access_token)

        return response, 200

    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/verify-token', methods=['GET'])
@jwt_required()
def verify_token():
    user =  db.session.get(User, get_jwt_identity())
    if not user:
        return jsonify({"error": "invalid user"}), 401
    department = db.session.get(
        Department, user.department_id) if user.department_id else None
    role = db.session.get(Role, user.role_id) if user.role_id else None
    return jsonify({
        "id": user.id,
        "fullname": user.fullname,
        "email": user.email,
        "department": department.name if department else "unknown department",
        "role": role.name if role else "unknown role",
        "payroll_no": user.payroll_no
    }), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    try:
        jwt_payload = get_jwt()
        jti = jwt_payload["jti"]
        token_type = jwt_payload["type"]
        expires = datetime.fromtimestamp(jwt_payload["exp"], tz=timezone.utc)

        revoked_token = RevokedToken(
            jti=jti,
            token_type=token_type,
            expires_at=expires,
            revoked_at=datetime.now(timezone.utc)
        )
        db.session.add(revoked_token)
        db.session.commit()

        response = jsonify({"message": "Successfully logged out"})
        unset_jwt_cookies(response)
        return response, 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/auth/update/<user_id>', methods=['PUT'])
#@jwt_required()
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
        if 'domain_id' in user_data:
            user.domain_id == user_info['domain_id']
        db.session.commit()
        department = Department.query.get(user.department_id)
        role = Role.query.get(user.role_id)
        if department:
            department_name = department.name
        else:
            department_name = "Unknown Department"
        role_name = role.name if role else "Unknown Role"
        domain = Domain.query.get(user.domain_id)
        if domain:
            domain_name = domain.name
        else:
            domain_name = "unknown domain"
        return jsonify({"Success": "User Updated",
                        "Details": {
                            "role_id": role_name,
                            "email": user.email,
                            "fullname": user.fullname,
                            "department_id": department_name,
                            "domain_id": domain_name
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
        current_user = db.session.get(User, get_jwt_identity())
        users = User.query.filter_by(domain_id=current_user.domain_id).all()
        user_list = []
        for user in users:
            department = db.session.get(
                Department, user.department_id) if user.department_id else None
            role = db.session.get(Role, user.role_id) if user.role_id else None
            user_list.append({
                "id": user.id,
                "fullname": user.fullname,
                "payroll_no": user.payroll_no,
                "email": user.email,
                "department": department.name if department else \
                    "Unknown Department",
                "role": role.name if role else "Unknown Role"
            })
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500