from flask import Blueprint, jsonify, request
import traceback
from flask_jwt_extended import jwt_required
from sqlalchemy import and_
from flask_jwt_extended import get_jwt_identity
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
                "error": "Unsupported Media Type: Content-Type must be application/json"
            }), 415
    
        current_user = db.session.get(User, get_jwt_identity())
        asset_data = request.get_json()
        asset_info = RegAssetSchema().load(asset_data)
    
        # --- Category-based Tag Generation ---
        category = db.session.get(Category, asset_info["category_id"])
        category_parts = category.name.split(':')
        category_prefix = category_parts[0][:4]
        category_suffix = category_parts[1][:3]
        base_tag = f"{category_prefix}{category_suffix}"
    
        latest_asset = Asset.query.filter(
            Asset.asset_tag.like(f"{base_tag}%"),
            Asset.domain_id == current_user.domain_id
        ).order_by(Asset.asset_tag.desc()).first()
    
        if latest_asset:
            last_number = int(latest_asset.asset_tag[-3:])
            new_number = str(last_number + 1).zfill(3)
        else:
            new_number = "001"
    
        asset_tag = f"{base_tag}{new_number}"
    
        # --- Name Generation (Domain Scoped) ---
        location = db.session.get(Location, asset_info["location_id"]).name[:4].upper()
        department = db.session.get(Department, asset_info["department_id"]).name[:4].upper()
        base_name = f"{location}-{department}-{category_suffix.upper()}"
    
        latest_asset_name = Asset.query.filter(
            Asset.name.like(f"{base_name}%"),
            Asset.domain_id == current_user.domain_id
        ).order_by(Asset.name.desc()).first()
    
        if latest_asset_name:
            last_number = int(latest_asset_name.name[-2:])
            new_number = str(last_number + 1).zfill(2)
        else:
            new_number = "01"
    
        asset_name = f"{base_name}{new_number}"
    
        # --- Create Asset ---
        new_asset = Asset(
            asset_tag=asset_tag,
            name=asset_name,
            serial_number=asset_info["serial_number"],
            model_number=asset_info["model_number"],
            category_id=asset_info["category_id"],
            assigned_to=asset_info["assigned_to"],
            location_id=asset_info.get("location_id"),
            status_id=asset_info.get("status_id"),
            purchase_date=asset_info.get("purchase_date"),
            warranty_expiry=asset_info.get("warranty_expiry"),
            configuration=asset_info.get("configuration"),
            department_id=asset_info.get("department_id"),
            domain_id=current_user.domain_id
        )
    
        db.session.add(new_asset)
        db.session.commit()
    
        return jsonify({
            "message": "Asset created successfully",
            "asset": new_asset.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        print("Exception occurred:")
        traceback.print_exc()
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
            
        current_user = db.session.get(User, get_jwt_identity())
        
        asset = Asset.query.filter_by(
            domain_id=current_user.domain_id, id=asset_id).first()
        if not asset:
            return jsonify({"error": "Asset not found or unauthorized"}), 404
        

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
            location = location.upper()
            department = db.session.get(
                Department, asset.department_id).name[:4]
            department = department.upper()

            base_name = f"{location}-{department}-{category_suffix.upper()}"
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
        current_user = db.session.get(User, get_jwt_identity())
        assets = Asset.query.filter_by(domain_id=current_user.domain_id).all()
        return jsonify({
            "assets": [a.to_dict() for a in assets],
            "total": len(assets)
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

 
@asset_bp.route("/assets/search", methods=["GET"])
@jwt_required()
def search_assets():
    """
    Search for assets based on various optional filters, including name,
    asset tag, serial number, model number, category, assigned user, location,
    and department. Automatically scoped to the current user's domain.
    
    Returns:
        - 200 OK: Paginated list of filtered assets.
        - 500 Internal Server Error: On unexpected exception.
    """
    try:
        query = (
            Asset.query
            .join(User, Asset.assigned_to == User.id, isouter=True)
            .join(Category, Asset.category_id == Category.id, isouter=True)
            .join(Location, Asset.location_id == Location.id, isouter=True)
            .join(
                Department, Asset.department_id == Department.id, isouter=True)
        )

        args = request.args
        mapping = {
            "name": Asset.name,
            "asset_tag": Asset.asset_tag,
            "serial_number": Asset.serial_number,
            "model_number": Asset.model_number,
            "category": Category.name,
            "assigned_to": User.fullname,
            "location": Location.name,
            "department": Department.name,
        }

        filters = []
        for key, column in mapping.items():
            value = args.get(key)
            if value:
                filters.append(column.ilike(f"%{value}%"))

        if filters:
            query = query.filter(and_(*filters))

        page = args.get("page", type=int, default=1)
        per_page = args.get("per_page", type=int, default=10)

        paginated = query.paginate(
            page=page, per_page=per_page, error_out=False)

        return jsonify({
            "assets": [asset.to_dict() for asset in paginated.items],
            "total": paginated.total,
            "page": paginated.page,
            "per_page": paginated.per_page,
            "pages": paginated.pages,
        }), 200

    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500

@asset_bp.route("/count/assets", methods=["GET"])
@jwt_required()
def get_inventory_counts():
    """
    Retrieve total counts of assets, consumables, and software
    filtered by the current user's domain.

    Returns:
        - 200 OK: JSON with domain-specific totals.
        - 401 Unauthorized: If user not found.
        - 500 Internal Server Error: On unexpected failure.
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = db.session.get(User, current_user_id)

        if not current_user:
            return jsonify({"error": "User not found"}), 401
        total_assets = Asset.query.filter_by(
            domain_id=current_user.domain_id).count()
        total_consumables = (
            db.session.query(func.sum(Consumables.quantity))
            .filter(Consumables.domain_id == current_user.domain_id)
            .scalar()
        ) or 0
        
        total_software = Software.query.filter_by(
            domain_id=current_user.domain_id).count()

        return jsonify({
            "totalAssets": total_assets,
            "totalConsumables": total_consumables,
            "totalSoftware": total_software
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


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
        current_user_id = get_jwt_identity()
        user = db.session.get(User, current_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        query = (
            db.session.query(Asset)
            .join(User, Asset.assigned_to == User.id)
            .join(Category, Asset.category_id == Category.id)
            .join(Location, Asset.location_id == Location.id)
            .join(Department, Asset.department_id == Department.id)
            .filter(Asset.domain_id == user.domain_id)
        )

        filters = []
        args = request.args
        mapping = {
            "name": Asset.name,
            "asset_tag": Asset.asset_tag,
            "serial_number": Asset.serial_number,
            "model_number": Asset.model_number,
            "category": Category.name,
            "assigned_to": User.fullname,
            "location": Location.name,
            "department": Department.name
        }

        for key, column in mapping.items():
            value = args.get(key)
            if value:
                filters.append(column.ilike(f"%{value}%"))

        if filters:
            query = query.filter(and_(*filters))

        assets_to_delete = query.all()
        if not assets_to_delete:
            return jsonify({
                "error": "No matching assets found for deletion"}), 404

        count = len(assets_to_delete)
        for asset in assets_to_delete:
            db.session.delete(asset)

        db.session.commit()
        return jsonify({
            "message": f"Successfully deleted {count} asset(s)."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
              "error": f"An unexpected error occurred: {str(e)}"}), 500
