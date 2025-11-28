from flask import Blueprint, request, jsonify, g
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, ma
from app.models.v1 import Consumables, User
from utils.validations.consumables.con_validate import (
    RegConSchema, UpdateConSchema)


consumables_bp = Blueprint("consumables_bp", __name__)


@consumables_bp.route('/register/consumable', methods=['POST'])
@jwt_required()
def register_consumable():
    """
    Registers a new consumable in the inventory
    Validates the request payload, ensures it is in JSON format, and
    stores the consumable in the database. Requires authentication.
    Returns:
        - 201 Created: Consumable successfully registered.
        - 400 Bad Request: Validation error.
        - 415 Unsupported Media Type: Invalid content type.
        - 500 Internal Server Error: Unexpected server error.

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
            return jsonify({"error": "Unauthorized"}), 401
        consumable_data = request.get_json()
        validated_consumable_info = RegConSchema().load(consumable_data)
        new_consumable = Consumables(
            name=validated_consumable_info['name'],
            category=validated_consumable_info['category'],
            brand=validated_consumable_info['brand'],
            model=validated_consumable_info['model'],
            quantity=validated_consumable_info['quantity'],
            unit_of_measure=validated_consumable_info['unit_of_measure'],
            reorder_level=validated_consumable_info['reorder_level'],
            location_id=validated_consumable_info['location_id'],
            domain_id=current_user.domain_id
        )
        db.session.add(new_consumable)
        db.session.commit()
        return jsonify({
            "message": "Consumable created successfully.",
            new_consumable.name: new_consumable.to_dict()
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500


@consumables_bp.route('/update/consumable/<int:id>', methods=['PUT'])
@jwt_required()
def update_consumable(id):
    """
    Updates the details of an existing consumable in the inventory.
    This endpoint allows an authenticated user to modify specific fields
    (name, category, brand, model, unit_of_measure, reorder_level) of
    a consumable item identified by its unique ID.
    Parameters:
        id (int): The ID of the consumable to be updated.
    Returns:
        Response (JSON):
            - 200 OK: If the consumable is successfully updated.
            - 400 Bad Request: If the input data is invalid.
            - 404 Not Found: If the consumable with the given
                ID does not exist.
            - 415 Unsupported Media Type: If the request is not in JSON format.
            - 500 Internal Server Error: For unexpected errors
                during processing.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        consumable = db.session.get(Consumables, id)
        if not consumable:
            return jsonify(
                {"error": f"Consumable with id {id} not found."}), 404
        consumable_data = request.get_json()
        validated_consumable_info = UpdateConSchema().load(consumable_data)
        if 'name' in validated_consumable_info:
            consumable.name = validated_consumable_info['name']
        if 'category' in validated_consumable_info:
            consumable.category = validated_consumable_info['category']
        if 'brand' in validated_consumable_info:
            consumable.brand = validated_consumable_info['brand']
        if 'model' in validated_consumable_info:
            consumable.model = validated_consumable_info['model']
        if 'unit_of_measure' in validated_consumable_info:
            consumable.unit_of_measure = validated_consumable_info[
                'unit_of_measure']
        if 'reorder_level' in validated_consumable_info:
            consumable.reorder_level = validated_consumable_info[
                'reorder_level']

        db.session.commit()
        return jsonify({
            "message": "Consumable updated successfully.",
            consumable.name: consumable.to_dict()
        }), 200
    except ValidationError as err:
        return jsonify({
            "error": err.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500


@consumables_bp.route('/consumable/<int:id>', methods=['Get'])
@jwt_required()
def get_consumable(id):
    """
    Retrieves a single consumable by its unique ID.
    This endpoint fetches a consumable resource from the database based on
    the provided ID. If the consumable exists, it returns the details as
    a JSON object. If the consumable is not found, a 404 error is automatically
    raised.
    Parameters:
        id (int): The unique ID of the consumable.
    Returns:
        Response (JSON):
            - 200 OK: If the consumable is found, returns
                the consumable details.
            - 404 Not Found: If the consumable with the provided
                ID does not exist.
            - 500 Internal Server Error: For unexpected errors
                during processing.
    """
    try:
        consumable = db.session.get(Consumables, id)
        if not consumable:
            return jsonify(
                {"error": f"Consumable with id {id} not found."}), 404
        return jsonify(consumable.to_dict()), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500


@consumables_bp.route('/consumables', methods=['GET'])
@jwt_required()
def get_all_consumable():
    """
    Retrieves all consumables in the inventory.
    This endpoint fetches all consumables from the database. If no consumables
    exist, a 404 error with a custom message is returned. If consumables
    are found, their details are returned as a list in JSON format.
    Returns:
        Response (JSON):
            - 200 OK: If consumables are found, returns a list of consumables.
            - 404 Not Found: If no consumables are found in the inventory.
            - 500 Internal Server Error: For unexpected errors during
                processing.
    """
    try:
        consumables = Consumables.query.all()
        if consumables:
            consumable_list = [
                consumable.to_dict() for consumable in consumables
            ]
            return jsonify({
                "consumables": consumable_list
            }), 200
        else:
            return jsonify({
                "error": "No consumable found"
            }), 404
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500


@consumables_bp.route('/consumable/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_consumable(id):
    """
    Deletes a consumable by its unique ID.
    This endpoint deletes a consumable resource from the database based on the
    provided ID. If the consumable exists, it is removed from the database.
    If the consumable does not exist, a 404 error is automatically raised.
    Parameters:
        id (int): The unique ID of the consumable to delete.
    Returns:
        Response (JSON):
            - 200 OK: If the consumable is successfully deleted.
            - 404 Not Found: If the consumable with the provided
                ID does not exist.
            - 500 Internal Server Error: For unexpected errors
                 during processing.
    """
    try:
        consumable = db.session.get(Consumables, id)
        if not consumable:
            return jsonify(
                {"error": f"Consumable with id {id} not found."}), 404
        db.session.delete(consumable)
        db.session.commit()
        return jsonify({
            "message": "Consumable deleted successfully."
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occured: {str(e)}"
        }), 500


@consumables_bp.route('/consumables/search', methods=['Get'])
@jwt_required()
def search_consumables():
    """
    Searches for consumables based on optional query parameters:
    'name', 'category', and 'brand'.
    Returns a list of consumables that match the provided search criteria.

    Query Parameters:
    - name (str): The name of the consumable to search for.
    - category (str): The category of the consumable to search for.
    - brand (str): The brand of the consumable to search for.

    Returns:
    - 200 OK: A JSON response containing a list of matching consumables.
    - 500 Internal Server Error: If an unexpected error occurs
        during the search process.
    """
    try:
        name = request.args.get('name', None)
        category = request.args.get('category', None)
        brand = request.args.get('brand', None)

        query = Consumables.query

        if name:
            query = query.filter(Consumables.name.ilike(f"%{name}%"))
        if category:
            query = query.filter(Consumables.category.ilike(f"%{category}%"))
        if brand:
            query = query.filter(Consumables.brand.ilike(f"%{brand}%"))

        consumables = query.all()

        return jsonify({
            "consumables":
            [consumable.to_dict() for consumable in consumables]
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500
