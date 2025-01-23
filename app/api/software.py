from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Software
from flask_jwt_extended import jwt_required
from utils.validations.software_validation import RegSoftwareSchema


sofware_bp = Blueprint("software_bp", __name__)


@sofware_bp.route("/register/software", methods=["POST"])
@jwt_required()
def create_software():
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        software_data = request.get_json()
        software_info = RegSoftwareSchema().load(software_data)
        new_software = Software(
            name=software_info["name"],
            version=software_info["version"],
            license_key=software_info["license_key"],
            expiry_date=software_info["expiry_date"],
        )
        db.session.add(new_software)
        db.session.commit()
        return jsonify({
            "message": "Software created successfully",
            "Software": {
                "name": new_software.name,
                "version": new_software.version,
                "license_key": new_software.license_key,
                "expiry_date": new_software.expiry_date
            }
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
            f"An unexpected error occurred: {str(e)}"
        }), 500
