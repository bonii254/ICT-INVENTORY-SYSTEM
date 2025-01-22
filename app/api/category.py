from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Category
from flask_jwt_extended import jwt_required
from utils.validations.cat_validate import RegCatSchema


cat_bp = Blueprint("cat_bp", __name__)


@cat_bp.route('/register/category', methods=['POST'])
@jwt_required()
def create_category():
    """
    Create a new category.

    This endpoint allows authenticated users to create a new category by providing
    the `name` and `description` in the request body. Validates input using a
    schema and saves the role to the database.

    Returns:
        - 201: category created successfully.
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
        cat_data = request.get_json()
        new_cat = RegCatSchema().load(cat_data)
        db.session.add(new_cat)
        db.session.commit()
        return jsonify({
            "message": "Category registered successfully!",
            "Category": {
                "name": new_cat.name,
                "description": new_cat.description
            }
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
