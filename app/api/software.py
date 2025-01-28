from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Software
from flask_jwt_extended import jwt_required
from utils.validations.software_validation import (RegSoftwareSchema,
                                                   UpdateSoftwareSchema)


sofware_bp = Blueprint("software_bp", __name__)


@sofware_bp.route("/register/software", methods=["POST"])
@jwt_required()
def create_software():
    """
    Registers a new software.
    Validates and processes the input JSON data to create a new software record
    in the database. A JWT token is required for authentication.
    Returns:
        JSON response:
            - 201: Software created successfully.
            - 400: Validation errors in the input data.
            - 415: Unsupported Media Type if the content type is not JSON.
            - 500: An unexpected server error occurred.
    """
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


@sofware_bp.route("/software/<int:software_id>", methods=["PUT"])
@jwt_required()
def update_software(software_id):
    """
    Updates an existing software record.
    Fetches a software record by ID and updates it with the provided input data.
    A JWT token is required for authentication.
    Args:
        software_id (int): The ID of the software to be updated.
    Returns:
        JSON response:
            - 200: Software updated successfully.
            - 400: Validation errors in the input data.
            - 404: Software with the specified ID was not found.
            - 415: Unsupported Media Type if the content type is not JSON.
            - 500: An unexpected server error occurred.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        software = Software.query.get(software_id)
        if not software:
            return jsonify({
                "error": f"Software with id {software_id} not found"
            }), 404
        software_data = request.get_json()
        software_info = UpdateSoftwareSchema().load(software_data)
        if 'name' in software_info:
            software.name = software_info['name']
        if 'version' in software_info:
            software.version = software_info['version']
        if 'license_key' in software_info:
            software.license_key = software_info['license_key']
        if 'expiry_date' in software_info:
            software.expiry_date =software_info['expiry_date']
        db.session.commit()
        return jsonify({
            "software": {
                "name": software.name,
                "version": software.version,
                "license_key": software.license_key,
                "expiry_date": software.expiry_date
            }
        }), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
            f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software", methods=["GET"])
@jwt_required()
def get_all_software(software_id):
    """
    Fetches all software records.
    Retrieves all software records from the database. A JWT token is required
    for authentication.
    Returns:
        JSON response:
            - 200: List of all software records.
            - 500: An unexpected server error occurred.
    """
    try:
        softwares = Software.query.all()
        software_list = [
            {
               "name": software.name,
                "version": software.version,
                "license_key": software.license_key,
                "expiry_date": software.expiry_date
            } for software in softwares
        ]
        return jsonify({
            "Softwares": software_list
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/<int:software_id>", methods=["DELETE"])
@jwt_required()
def delete_software(software_id):
    """
    Deletes a software record by ID.
    Fetches a software record by ID and deletes it from the database.
    A JWT token is required for authentication.
    Args:
        software_id (int): The ID of the software to be deleted.
    Returns:
        JSON response:
            - 201: Software deleted successfully.
            - 404: Software with the specified ID was not found.
            - 500: An unexpected server error occurred.
    """
    try:
        software = Software.query.get(software_id)
        if not software:
            return jsonify({
                "error": "Software with id {software_id} not found"
            }), 404
        db.session.delete(software)
        db.session.commit()
        return jsonify({
                "Message": "software deleted successfully"
            }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
