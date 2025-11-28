from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import and_
from app.extensions import db
from app.models.v1 import ExternalMaintenance, Asset, Provider, User
from utils.validations.external_validate import (
    ExternalMaintenanceCreateSchema,
    ExternalMaintenanceUpdateSchema)
    

maintenance_bp = Blueprint("maintenance", __name__)


@maintenance_bp.route("/maintenance", methods=["POST"])
@jwt_required()
def create_maintenance():
    """Register a new external maintenance record."""
    try:
        data = request.get_json()
        validated = ExternalMaintenanceCreateSchema().load(data)
        maintenance = ExternalMaintenance(**validated)
        maintenance.save()

        return jsonify({
            "message": "Maintenance record created successfully",
            "maintenance": maintenance.to_dict()
        }), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@maintenance_bp.route("/maintenance", methods=["GET"])
@jwt_required()
def list_maintenance():
    """Retrieve all maintenance records (domain scoped)."""
    try:
        records = ExternalMaintenance.query.all()
        return jsonify([m.to_dict() for m in records]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["GET"])
@jwt_required()
def get_maintenance(maintenance_id):
    """Retrieve a single maintenance record by ID."""
    record = ExternalMaintenance.query.get(maintenance_id)
    if not record:
        return jsonify({"error": "Maintenance record not found"}), 404
    return jsonify(record.to_dict()), 200


@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["PUT"])
@jwt_required()
def update_maintenance(maintenance_id):
    """Update details of an existing maintenance record."""
    record = ExternalMaintenance.query.get(maintenance_id)
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


@maintenance_bp.route("/maintenance/<int:maintenance_id>", methods=["DELETE"])
@jwt_required()
def delete_maintenance(maintenance_id):
    """Delete a maintenance record."""
    record = ExternalMaintenance.query.get(maintenance_id)
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
