from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
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
    Fetches a software record by ID and updates it with the provided
    input data.
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
            software.expiry_date = software_info['expiry_date']
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


@sofware_bp.route("/softwares", methods=["GET"])
@jwt_required()
def get_all_software():
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
        software_list = [software.to_dict() for software in softwares]
        return jsonify({
            "Softwares": software_list
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/search", methods=["GET"])
@jwt_required()
def search_software():
    """
    Searches software records by name, version, or license key.
    Query Parameters:
        - name (str): Name of the software.
        - version (str): Version of the software.
        - license_key (str): License key of the software.
    Returns:
        JSON response:
            - 200: Matching software records.
            - 400: Validation errors in query parameters.
            - 500: An unexpected server error occurred.
    """
    try:
        name = request.args.get("name", None)
        version = request.args.get("version", None)
        license_key = request.args.get("license_key", None)

        query = Software.query
        if name:
            query = query.filter(Software.name.ilike(f"%{name}%"))
        if version:
            query = query.filter(Software.version.ilike(f"%{version}%"))
        if license_key:
            query = query.filter(
                Software.license_key.ilike(f"%{license_key}%"))

        softwares = query.all()
        software_list = [software.to_dict() for software in softwares]
        return jsonify({
            "Softwares": software_list
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/license-status", methods=["GET"])
@jwt_required()
def check_license_status():
    """
    Fetches software records with licenses that are expired or expiring soon.
    Query Parameters:
        - days (int): Number of days to check for expiration (default: 30).
    Returns:
        JSON response:
            - 200: Software records with expired or soon-to-expire licenses.
            - 500: An unexpected server error occurred.
    """
    try:
        days = int(request.args.get("days", 30))
        current_date = datetime.utcnow()
        threshold_date = current_date + timedelta(days=days)

        expiring_licenses = Software.query.filter(
            Software.expiry_date <= threshold_date
        ).all()
        software_list = [software.to_dict() for software in expiring_licenses]
        return jsonify({
            "Softwares": software_list,
            "Message":
            f"Software with licenses expiring in the next {days} days"
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/bulk-register", methods=["POST"])
@jwt_required()
def bulk_register_software():
    """
    Registers multiple software records in bulk.
    Request Body:
        - List of software records (each with name, version, license_key,
        expiry_date).
        Returns:
        JSON response:
            - 201: Successfully created all software records.
            - 400: Validation errors in one or more software records.
            - 500: An unexpected server error occurred.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415

        software_data_list = request.get_json()
        software_schema = RegSoftwareSchema(many=True)
        software_list = software_schema.load(software_data_list)

        new_software_objects = [
            Software(
                name=software["name"],
                version=software["version"],
                license_key=software["license_key"],
                expiry_date=software["expiry_date"],
            )
            for software in software_list
        ]

        db.session.bulk_save_objects(new_software_objects)
        db.session.commit()

        return jsonify({
            "message": "All software records created successfully"
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/expiry", methods=["GET"])
@jwt_required()
def get_software_by_expiry_range():
    """
    Fetches software records expiring within a specific date range.
    Query Parameters:
        - start_date (str): Start of the date range (format: YYYY-MM-DD).
        - end_date (str): End of the date range (format: YYYY-MM-DD).
    Returns:
        JSON response:
            - 200: Software records expiring in the specified range.
            - 400: Validation errors in the query parameters.
            - 500: An unexpected server error occurred.
    """
    try:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return jsonify({
                "error": "Both 'start_date' and 'end_date' are required."
            }), 400

        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        software_in_range = Software.query.filter(
            Software.expiry_date.between(start_date, end_date)
        ).all()

        software_list = [software.to_dict() for software in software_in_range]

        return jsonify({
            "Softwares": software_list
        }), 200
    except ValueError:
        return jsonify({
            "error": "Invalid date format. Use YYYY-MM-DD."
        }), 400
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@sofware_bp.route("/software/report", methods=["GET"])
@jwt_required()
def generate_software_report():
    """
    Generates a detailed software report.
    Query Parameters:
        - name (str, optional): Filter by name.
        - expired_only (bool, optional): Include only expired software.
        - start_date (str, optional): Start of the date range
        (format: YYYY-MM-DD).
        - end_date (str, optional): End of the date range (format: YYYY-MM-DD).
    Returns:
        JSON response:
            - 200: A detailed software report.
            - 400: Validation errors in the query parameters.
            - 500: An unexpected server error occurred.
    """
    try:
        name = request.args.get("name", None)
        expired_only = request.args.get(
            "expired_only", "false").lower() == "true"
        start_date = request.args.get("start_date", None)
        end_date = request.args.get("end_date", None)

        query = Software.query
        if name:
            query = query.filter(Software.name.ilike(f"%{name}%"))
        if expired_only:
            query = query.filter(Software.expiry_date < datetime.utcnow())
        if start_date and end_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(
                Software.expiry_date.between(start_date, end_date))

        softwares = query.all()
        software_list = [software.to_dict() for software in softwares]

        return jsonify({
            "Report": software_list
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
