from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Category, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from utils.validations.cat_validate import RegCatSchema, UpdateCatSchema


cat_bp = Blueprint("cat_bp", __name__)


@cat_bp.route('/register/category', methods=['POST'])
@jwt_required()
def create_category():
    """
    Create a new category.

    This endpoint allows authenticated users to create a new category
    by providing the `name` and `description` in the request body.
    Validates input using a schema and saves the role to the database.

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
                "error": "Unsupported Media Type. \
                    Content-Type must be application/json."
            }), 415
        current_user = db.session.get(User, get_jwt_identity())
        cat_data = request.get_json()
        cat_info = RegCatSchema().load(cat_data)
        new_cat = Category(
            name = cat_info["name"].capitalize(),
            description = cat_info["description"],
            domain_id = current_user.domain_id
        )
        db.session.add(new_cat)
        db.session.commit()
        return jsonify({
            "category": {
                "id": new_cat.id,
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


@cat_bp.route('/category/<int:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    """
    Update a category's details by ID.
    Args:
        category_id (int): The ID of the category to update.
    Returns:
        JSON response with the updated category details,
        or an error message if unsuccessful.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        current_user = db.session.get(User, get_jwt_identity())
        category = Category.query.filter_by(
            domain_id=current_user.domain_id, id=category_id).first()
        if not category:
            return jsonify({
                "error": f"category with ID {category_id} not found."
            }), 404
        category_data = request.get_json()
        validated_category = UpdateCatSchema().load(category_data)
        if 'name' in validated_category:
            category.name = validated_category['name'].capitalize()
        if 'description' in validated_category:
            category.description = validated_category['description']
        db.session.commit()
        return jsonify({
            "Message": "category updated successfully",
            "category": {
                "id:": category.id,
                "name": category.name,
                "description": category.description
            }
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@cat_bp.route('/category/<category_id>', methods=['GET'])
@jwt_required()
def get_category(category_id):
    """
    Retrieve a category by ID.
    Args:
        category_id (str): The numeric ID of the category.
    Returns:
        - 200: JSON with category details if found.
        - 400: JSON error for invalid ID format.
        - 404: JSON error if category not found.
        - 500: JSON error for server issues.
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        category = Category.query.filter_by(
            domain_id=current_user.domain_id, id=category_id).first()
        if category:
            return jsonify({
                "category": {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description
                }
            }), 200
        return jsonify({
            "Error": f"category with id {category_id} does not exist"
        }), 404
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@cat_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_all_categories():
    """
    Retrieve all categories.
    Returns:
        JSON response with a list of all categories,
        or an error message if unsuccessful.
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        categories = Category.query.filter_by(domain_id=current_user.domain_id)
        category_list = [
            {
                "id": category.id,
                "name": category.name,
                "description": category.description
            } for category in categories
        ]
        return jsonify(category_list), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@cat_bp.route('/category/<int:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    """
    Delete a category by ID.
        Args:
    category_id (int): The ID of the category to delete.
    Returns:
        JSON response confirming deletion,
        or an error message if the category does not exist.
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        category = Category.query.filter_by(
            domain_id=current_user.domain_id, id=category_id).first()
        if category:
            db.session.delete(category)
            db.session.commit()
            return jsonify({
                "Message": "category deleted successfully"
            }), 200
        return jsonify({
            "Error": f"category with id {category_id} does not exist"
        }), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
