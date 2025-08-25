from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import and_
from marshmallow import ValidationError
from app.models.v1 import (Asset, User, Location, Department, Status, Category,
                           Consumables, Software)
from app.extensions import db
from utils.validations.asset_validate import RegAssetSchema, UpdateAssetSchema
from sqlalchemy import func


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
        category = db.session.get(Category, asset_info["category_id"])
        category_parts = category.name.split(':')
        category_prefix = category_parts[0][:4]
        category_suffix = category_parts[1][:3]
        base_tag = f"{category_prefix}{category_suffix}"
        latest_asset = Asset.query.filter(
            Asset.asset_tag.like(f"{base_tag}%")).order_by(
                Asset.asset_tag.desc()).first()
        if latest_asset:
            last_number = int(latest_asset.asset_tag[-3:])
            new_number = str(last_number + 1).zfill(3)
        else:
            new_number = "001"
        asset_tag = f"{base_tag}{new_number}"

        location = db.session.get(Location, asset_info["location_id"]).name[:4]
        location = location.capitalize()
        department = db.session.get(
            Department, asset_info["department_id"]).name[:4]
        department = department.capitalize()
        base_name = f"{location}-{department}-{category_suffix.capitalize()}"
        latest_asset_name = Asset.query.filter(
            Asset.name.like(f"{base_name}%")).order_by(
                Asset.name.desc()).first()
        if latest_asset_name:
            last_number = int(latest_asset_name.name[-2:])
            new_number = str(last_number + 1).zfill(2)
        else:
            new_number = "01"
        asset_name = f"{base_name}{new_number}"
        new_asset = Asset(
            asset_tag=asset_tag,
            name=asset_name,
            serial_number=asset_info["serial_number"],
            model_number=asset_info["model_number"],
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

        user = db.session.get(User, new_asset.assigned_to)
        location = db.session.get(Location, new_asset.location_id)
        department = db.session.get(Department, new_asset.department_id)
        status = db.session.get(Status, new_asset.status_id)

        return jsonify({
            "message": "Asset created successfully",
            "asset": {
                "asset_tag": new_asset.asset_tag,
                "name": new_asset.name,
                "serial_number": new_asset.serial_number,
                "model_number": new_asset.model_number,
                "category": category.name,
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


@asset_bp.route("/update/asset/<int:asset_id>", methods=["PUT"])
@jwt_required()
def update_asset(asset_id):
    """
    Update an existing asset.
    Regenerates asset_tag and name if category, location,
    or department changes.
    Returns:
        - 200: Asset updated successfully.
        - 400: Validation error.
        - 404: Asset not found.
        - 415: Unsupported Media Type.
        - 500: Internal server error.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        asset = db.session.get(Asset, asset_id)
        if not asset:
            return jsonify({"error": "Asset not found"}), 404

        update_data = request.get_json()
        asset_info = UpdateAssetSchema().load(update_data)
        category_changed = "category_id" in asset_info \
            and asset_info["category_id"] != asset.category_id
        location_changed = "location_id" in asset_info \
            and asset_info["location_id"] != asset.location_id
        department_changed = "department_id" in asset_info \
            and asset_info["department_id"] != asset.department_id

        for field, value in asset_info.items():
            setattr(asset, field, value)

        if category_changed or location_changed or department_changed:
            category = db.session.get(Category, asset.category_id)
            if not category:
                return jsonify({"error": "Invalid category"}), 400

            category_parts = category.name.split(':')
            category_prefix = category_parts[0][:4]
            category_suffix = category_parts[1][:3]
            base_tag = f"{category_prefix}{category_suffix}"

            latest_asset = Asset.query.filter(
                Asset.asset_tag.like(f"{base_tag}%")
            ).order_by(Asset.asset_tag.desc()).first()

            if latest_asset:
                last_number = int(latest_asset.asset_tag[-3:])
                new_number = str(last_number + 1).zfill(3)
            else:
                new_number = "001"

            asset.asset_tag = f"{base_tag}{new_number}"

            location = db.session.get(Location, asset.location_id).name[:4]
            location = location.capitalize()
            department = db.session.get(
                Department, asset.department_id).name[:4]
            department = department.capitalize()

            base_name = f"{location}-{department}-{category_suffix.capitalize()}"
            latest_asset_name = Asset.query.filter(
                Asset.name.like(f"{base_name}%")
            ).order_by(Asset.name.desc()).first()

            if latest_asset_name:
                last_number = int(latest_asset_name.name[-2:])
                new_number = str(last_number + 1).zfill(2)
            else:
                new_number = "01"

            asset.name = f"{base_name}{new_number}"

        db.session.commit()

        category = db.session.get(Category, asset.category_id)
        user = db.session.get(User, asset.assigned_to)
        location = db.session.get(Location, asset.location_id)
        department = db.session.get(Department, asset.department_id)
        status = db.session.get(Status, asset.status_id)

        return jsonify({
            "message": "Asset updated successfully",
            "asset": {
                "asset_tag": asset.asset_tag,
                "name": asset.name,
                "serial_number": asset.serial_number,
                "model_number": asset.model_number,
                "category": category.name if category else None,
                "assigned_to": user.fullname if user else None,
                "location": location.name if location else None,
                "status": status.name if status else None,
                "purchase_date": asset.purchase_date,
                "warranty_expiry": asset.warranty_expiry,
                "configuration": asset.configuration,
                "department": department.name if department else None
            }
        }), 200

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@asset_bp.route("/assets", methods=["GET"])
@jwt_required()
def get_all_asset():
    """
    Retrieve all assets from the database.
    Returns:
        - 200 OK: A JSON response containing a list of all assets.
        - 500 Internal Server Error: If an exception occurs.
    """
    try:
        assets = Asset.query.all()
        total = Asset.query.count()
        return jsonify({
            "assets": [asset.to_dict() for asset in assets],
            "total": total}), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@asset_bp.route("/assets/search", methods=["GET"])
@jwt_required()
def search_assets():
    """
    Search for assets based on various optional filters, including name,
    asset tag, IP address, MAC address, category, assigned user, location,
    and department.

    Returns:
        - 200 OK: A paginated list of assets matching the filters.
        - 500 Internal Server Error: If an exception occurs.
    """
    try:
        name = request.args.get('name', None, type=str)
        asset_tag = request.args.get('asset_tag', None, type=str)
        serial_number = request.args.get('serial_number', None, type=str)
        model_number = request.args.get('model_number', None, type=str)
        category = request.args.get('category', None, type=str)
        assigned_to = request.args.get('assigned_to', None, type=str)
        location = request.args.get('location', None, type=str)
        department = request.args.get('department', None, type=str)
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=10)

        query = (
            db.session.query(Asset)
            .join(User, Asset.assigned_to == User.id)
            .join(Category, Asset.category_id == Category.id)
            .join(Location, Asset.location_id == Location.id)
            .join(Department, Asset.department_id == Department.id)
        )

        filters = []

        if name:
            filters.append(Asset.name.ilike(f"%{name}%"))
        if asset_tag:
            filters.append(Asset.asset_tag.ilike(f"%{asset_tag}%"))
        if serial_number:
            filters.append(Asset.serial_number.ilike(f"%{serial_number}%"))
        if model_number:
            filters.append(Asset.model_number.ilike(f"%{model_number}%"))
        if category:
            filters.append(Category.name.ilike(f"%{category}%"))
        if assigned_to:
            filters.append(User.fullname.ilike(f"%{assigned_to}%"))
        if location:
            filters.append(Location.name.ilike(f"%{location}%"))
        if department:
            filters.append(Department.name.ilike(f"%{department}%"))

        if filters:
            query = query.filter(and_(*filters))

        assets = query.paginate(page=page, per_page=per_page, error_out=False)

        response = {
            "assets": [asset.to_dict() for asset in assets.items],
            "total": assets.total,
            "page": assets.page,
            "per_page": assets.per_page,
            "pages": assets.pages
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@asset_bp.route("/count/assets", methods=["GET"])
@jwt_required()
def get_inventory_counts():
    """
    Retrieve the total count of assets, consumables, and software.
    Returns:
        - 200 OK: A JSON response containing the total counts for assets, consumables, and software.
        - 500 Internal Server Error: If an exception occurs.
    """
    try:
        total_assets = Asset.query.count()
        total_consumables = db.session.query(
            func.sum(Consumables.quantity)).scalar()
        if total_consumables is None:
            total_consumables = 0
        total_software = Software.query.count()

        return jsonify({
            "totalAssets": total_assets,
            "totalConsumables": total_consumables,
            "totalSoftware": total_software
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@asset_bp.route("/delete/assets", methods=["DELETE"])
@jwt_required()
def delete_assets():
    """
    Delete assets based on various optional filters.
    Returns:
        - 200 OK: Confirmation of deletion with count.
        - 404 Not Found: No matching assets found.
        - 500 Internal Server Error: If an exception occurs.
    """
    try:
        name = request.args.get('name', None, type=str)
        asset_tag = request.args.get('asset_tag', None, type=str)
        serial_number = request.args.get('serial_number', None, type=str)
        model_number = request.args.get('model_number', None, type=str)
        category = request.args.get('category', None, type=str)
        assigned_to = request.args.get('assigned_to', None, type=str)
        location = request.args.get('location', None, type=str)
        department = request.args.get('department', None, type=str)
        query = (
            db.session.query(Asset)
            .join(User, Asset.assigned_to == User.id)
            .join(Category, Asset.category_id == Category.id)
            .join(Location, Asset.location_id == Location.id)
            .join(Department, Asset.department_id == Department.id)
        )

        filters = []

        if name:
            filters.append(Asset.name.ilike(f"%{name}%"))
        if asset_tag:
            filters.append(Asset.asset_tag.ilike(f"%{asset_tag}%"))
        if serial_number:
            filters.append(Asset.serial_number.ilike(f"%{serial_number}%"))
        if model_number:
            filters.append(Asset.model_number.ilike(f"%{model_number}%"))
        if category:
            filters.append(Category.name.ilike(f"%{category}%"))
        if assigned_to:
            filters.append(User.fullname.ilike(f"%{assigned_to}%"))
        if location:
            filters.append(Location.name.ilike(f"%{location}%"))
        if department:
            filters.append(Department.name.ilike(f"%{department}%"))

        if filters:
            query = query.filter(and_(*filters))
        assets_to_delete = query.all()
        if not assets_to_delete:
            return jsonify(
                {"error": "No matching assets found for deletion"}), 404
        deleted_count = len(assets_to_delete)
        for asset in assets_to_delete:
            db.session.delete(asset)
        db.session.commit()
        return jsonify({
            "message": f"Successfully deleted {deleted_count} asset(s)."
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
