from flask import Blueprint, request, jsonify
import traceback
from datetime import date
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import and_
from app.extensions import db
from app.models.v1 import ExternalMaintenance, Asset, Provider, User
from utils.validations.external_validate import (
    ExternalMaintenanceCreateSchema,
    ExternalMaintenanceUpdateSchema)
from utils.token_helpers import generate_receipt_number
    

maintenance_bp = Blueprint("maintenance", __name__)


@maintenance_bp.route("/register/maintenance", methods=["POST"])
@jwt_required()
def create_maintenance():
    """Register a new external maintenance record."""
    try:
        if not request.is_json:
            return jsonify({
                "error": 
                    "Unsupported Media Type. Content-Type must be application/json."
            }), 415

        current_user = db.session.get(User, get_jwt_identity())
        data = request.get_json()
        if data["parent_asset_id"] == 0:
            data["parent_asset_id"] = None

        validated = ExternalMaintenanceCreateSchema().load(data)
        validated["domain_id"] = current_user.domain_id

        asset = db.session.get(Asset, validated["asset_id"])
        if not asset or asset.domain_id != current_user.domain_id:
            return jsonify({"error": "Asset not found or unauthorized"}), 404

        provider = db.session.get(Provider, validated["provider_id"])
        if not provider or provider.domain_id != current_user.domain_id:
            return jsonify({"error": "Provider not found or unauthorized"}), 404

        validated["receipt_number"] = generate_receipt_number(
            current_user.domain.name)

        maintenance = ExternalMaintenance(**validated)
        db.session.add(maintenance)
        db.session.commit()

        return jsonify({
            "message": "Maintenance record created successfully.",
            "maintenance": maintenance.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    except Exception as e:
        db.session.rollback()
        print("Exception occurred:")
        traceback.print_exc()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@maintenance_bp.route("/maintenance", methods=["GET"])
@jwt_required()
def list_maintenance():
    """Retrieve all maintenance records (domain scoped)."""
    try:
        current_user = db.session.get(User, get_jwt_identity())
        records = ExternalMaintenance.query.filter_by(
            domain_id=current_user.domain_id).all()
        return jsonify([m.to_dict() for m in records]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["GET"])
@jwt_required()
def get_maintenance(maintenance_id):
    """Retrieve a single maintenance record by ID."""
    current_user = db.session.get(User, get_jwt_identity())
    record = ExternalMaintenance.query.filter_by(
        domain_id=current_user.domain_id, id=maintenance_id).first()
    if not record:
        return jsonify({"error": "Maintenance record not found"}), 404
    return jsonify(record.to_dict()), 200


@maintenance_bp.route(
    "/maintenance/update/<int:maintenance_id>", methods=["PUT"])
@jwt_required()
def update_maintenance(maintenance_id):
    """Update details of an existing maintenance record."""
    current_user = db.session.get(User, get_jwt_identity())
    record = ExternalMaintenance.query.filter_by(
        domain_id=current_user.domain_id, id=maintenance_id).first()
    if not record:
        return jsonify({"error": "Maintenance record not found"}), 404

    try:
        data = request.get_json()
        validated = ExternalMaintenanceUpdateSchema().load(data, partial=True)
        for key, value in validated.items():
            setattr(record, key, value)
        db.session.commit()

        return jsonify({
            "message": "Maintenance record updated successfully",
            "maintenance": record.to_dict()
        }), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    
@maintenance_bp.route("/maintenance/receive/<int:maintenance_id>", methods=["PUT"])
@jwt_required()
def receive_asset(maintenance_id):
    """Mark an external maintenance asset as returned from provider."""
    current_user = db.session.get(User, get_jwt_identity())
    record = ExternalMaintenance.query.filter_by(
        domain_id=current_user.domain_id, id=maintenance_id
    ).first()

    if not record:
        return jsonify({"error": "Maintenance record not found"}), 404

    try:
        data = request.get_json() or {}
        validated = ExternalMaintenanceUpdateSchema().load(data, partial=True)

        if "actual_cost" in validated:
            record.actual_cost = validated["actual_cost"]
        if "actual_return_date" in validated:
            record.actual_return_date = validated["actual_return_date"]
        if "Condition_After_Maintenance" in validated:
            record.Condition_After_Maintenance = validated["Condition_After_Maintenance"]
        if "delivery_note" in validated:
            record.delivery_note = validated["delivery_note"]

        record.received_by = current_user.fullname
        record.status = "RETURNED"

        db.session.commit()

        return jsonify({
            "message": "Asset successfully marked as returned",
            "maintenance": record.to_dict()
        }), 200

    except ValidationError as ve:
        return jsonify({"errors": ve.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["DELETE"])
@jwt_required()
def delete_maintenance(maintenance_id):
    """Delete a maintenance record."""
    current_user = db.session.get(User, get_jwt_identity())
    record = ExternalMaintenance.query.filter_by(
        domain_id=current_user.domain_id, id=maintenance_id).first()
    if not record:
        return jsonify({"error": "Maintenance record not found"}), 404
    record.delete()
    return jsonify({"message": "Maintenance record deleted successfully"}), 200


@maintenance_bp.route("/maintenance/search", methods=["GET"])
@jwt_required()
def search_maintenance():
    """
    Search maintenance records by filters:
    - provider_name, asset_name, status, maintenance_type, date range
    """
    try:
        query = (
            db.session.query(ExternalMaintenance)
            .join(Asset, ExternalMaintenance.asset_id == Asset.id)
            .join(
                Provider, 
                ExternalMaintenance.provider_id == Provider.id, isouter=True)
        )

        filters = []
        args = request.args
        if provider := args.get("provider_name"):
            filters.append(Provider.name.ilike(f"%{provider}%"))
        if asset := args.get("asset_name"):
            filters.append(Asset.name.ilike(f"%{asset}%"))
        if status := args.get("status"):
            filters.append(ExternalMaintenance.status == status)
        if mtype := args.get("maintenance_type"):
            filters.append(ExternalMaintenance.maintenance_type == mtype)
        if start := args.get("start_date"):
            filters.append(
                ExternalMaintenance.sent_date >= datetime.fromisoformat(start))
        if end := args.get("end_date"):
            filters.append(
                ExternalMaintenance.sent_date <= datetime.fromisoformat(end))

        if filters:
            query = query.filter(and_(*filters))

        results = query.all()
        return jsonify([r.to_dict() for r in results]), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
