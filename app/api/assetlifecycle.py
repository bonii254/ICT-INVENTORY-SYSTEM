from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import AssetLifecycle
from utils.validations.alc_validate import RegAlcSchema


alc_bp = Blueprint("als_bp", __name__)


@alc_bp.route("/register/assetlifecycle", methods=["POST"])
@jwt_required()
def create_alc():
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        alc_data = request.get_json()
        alc_info = RegAlcSchema().load(alc_data)
        new_alc = AssetLifecycle(
            asset_id=alc_info["asset_id"],
            event=alc_info["event"],
            notes=alc_info["notes"]
        )
        db.session.add(new_alc)
        db.session.commit()
        return jsonify({
            "message": "AssetLifeCycle created successfully"
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
            f"An unexpected error occurred: {str(e)}"
        }), 500
