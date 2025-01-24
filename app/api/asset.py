from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.models.v1 import Asset, User, Location, Department, Status
from app.extensions import db
from utils.validations.asset_validate import RegAssetSchema


asset_bp = Blueprint("asset_bp", __name__)


@asset_bp.route("/register/asset", methods=["POST"])
@jwt_required()
def create_asset():
    """
    Register a new asset.

    This endpoint allows authorized users to register
    a new asset in the system.
    The request must contain a JSON payload with the following fields:
        - asset_tag (str): Unique identifier for the asset.
        - name (str): Name of the asset.
        - category_id (int): ID of the asset category.
        - assigned_to (int): ID of the user or entity the asset is assigned to.
        - location_id (int): ID of the location where the asset is situated.
        - status_id (int): ID of the current status of the asset.
        - purchase_date (str): Date when the asset was purchased (YYYY-MM-DD).
        - warranty_expiry (str): Warranty expiration date (YYYY-MM-DD).
        - configuration (str): Configuration details of the asset.
        - department_id (int): ID of the department owning the asset.

    Returns:
        - 201: Asset created successfully with asset details in the response.
        - 400: Validation error with details of the invalid fields.
        - 415: Unsupported Media Type error if the content type is not JSON.
        - 500: Internal server error in case of an unexpected issue.

    Requires:
        - JWT authorization.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        asset_data = request.get_json()
        asset_info = RegAssetSchema().load(asset_data)
        new_asset = Asset(
            asset_tag=asset_info["asset_tag"],
            name=asset_info["name"],
            ip_address=asset_info["ip_address"],
            mac_address=asset_info["mac_address"],
            category_id=asset_info["category_id"],
            assigned_to=asset_info["assigned_to"],
            location_id=asset_info["location_id"],
            status_id=asset_info["status_id"],
            purchase_date=asset_info["purchase_date"],
            warranty_expiry=asset_info["warranty_expiry"],
            configuration=asset_info["configuration"],
            department_id=asset_info["department_id"]
        )
        db.session.add(new_asset)
        db.session.commit()
        user = User.query.get(new_asset.assigned_to)
        location = Location.query.get(new_asset.location_id)
        department = Department.query.get(new_asset.department_id)
        status = Status.query.get(new_asset.status_id)

        return jsonify({
            "message": "Asset created successfully",
            "asset": {
                "asset_tag": new_asset.asset_tag,
                "name": new_asset.name,
                "ip_address": new_asset.ip_address,
                "mac_address": new_asset.mac_address,
                "category_id": new_asset.category_id,
                "assigned_to": user.fullname,
                "location": location.name,
                "status": status.name,
                "purchase_date": new_asset.purchase_date,
                "warranty_expiry": new_asset.warranty_expiry,
                "configuration": new_asset.configuration,
                "department": department.name
            }
        }), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
