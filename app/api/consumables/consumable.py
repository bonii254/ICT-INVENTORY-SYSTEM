from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from app.extensions import db, ma
from app.models.v1 import Consumables
from utils.validations.consumables.con_validate import RegConSchema


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
        consumable_data = request.get_json()
        validated_consumable_info = RegConSchema().load(consumable_data)
        new_consumable = Consumables(
            name=validated_consumable_info['name'],
            category=validated_consumable_info['category'],
            brand=validated_consumable_info['brand'],
            model=validated_consumable_info['model'],
            unit_of_measure=validated_consumable_info['unit_of_measure'],
            reorder_level=validated_consumable_info['reorder_level']
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
            "error": f"An unexpected erroroccured: {str(e)}"
        }), 500
