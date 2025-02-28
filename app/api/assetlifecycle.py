from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import AssetLifecycle, Asset
from utils.validations.alc_validate import RegAlcSchema, UpdateAlcSchema


alc_bp = Blueprint("als_bp", __name__)


@alc_bp.route("/register/assetlifecycle", methods=["POST"])
@jwt_required()
def create_alc():
    """
    Endpoint to create a new Asset Lifecycle record.
    This endpoint requires the user to be authenticated via JWT and sends
    a JSON payload with asset lifecycle data. If the data is valid, a new
    AssetLifecycle record is created and committed to the database.
    Returns:
        Response: JSON response indicating the success or failure of the
        operation
    """
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
            event=alc_info.get("event"),
            notes=alc_info.get("notes")
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


@alc_bp.route("/asset-lifecycles", methods=["GET"])
@jwt_required()
def get_all_asset_lifecycles():
    """
    Endpoint to retrieve all Asset Lifecycle records.
    This endpoint requires the user to be authenticated via JWT. It retrieves
    and returns a list of all asset lifecycle records from the database.
    Returns:
        Response: JSON array of asset lifecycle records.
    """
    try:
        events = AssetLifecycle.query.all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles/<int:event_id>", methods=["GET"])
@jwt_required()
def get_asset_lifecycle(event_id):
    """
    Endpoint to retrieve a specific Asset Lifecycle record by its ID.
    This endpoint requires the user to be authenticated via JWT. It retrieves
    a specific asset lifecycle record based on the provided event ID.
    Args:
        event_id (int): The ID of the asset lifecycle event to retrieve.
    Returns:
        Response: JSON object of the requested asset lifecycle record.
    """
    try:
        event = db.session.get(AssetLifecycle, event_id)
        if not event:
            return jsonify({
                "error": f"Assetlifecycle with id {event_id} not found."
            }), 404
        return jsonify(event.to_dict()), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/assets/<int:asset_id>/lifecycles", methods=["GET"])
@jwt_required()
def get_asset_lifecycles_by_asset(asset_id):
    """
    Endpoint to retrieve all Asset Lifecycle records for a specific asset.
    This endpoint requires the user to be authenticated via JWT. It retrieves
    all asset lifecycle records for a specified asset ID.
    Args:
        asset_id (int): The ID of the asset to retrieve lifecycle records for.
    Returns:
        Response: JSON array of asset lifecycle records for the specified
        asset.
    """
    try:
        asset = db.session.get(Asset, asset_id)
        if not asset:
            return jsonify({
                "error": f"Asset with id {asset_id} not found."
            }), 404
        events = AssetLifecycle.query.filter_by(asset_id=asset_id).all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_asset_lifecycle(event_id):
    """
    Endpoint to update an existing Asset Lifecycle record by its ID.
    This endpoint requires the user to be authenticated via JWT and sends a
    JSON payload to update the specified asset lifecycle event. The event data
    is validated and updated in the database.
    Args:
        event_id (int): The ID of the asset lifecycle event to update.
    Returns:
        Response: JSON object of the updated asset lifecycle record.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        event = db.session.get(AssetLifecycle, event_id)
        if not event:
            return jsonify({
                "error": f"Event with id {event_id} not found."
            }), 404
        data = request.get_json()
        validated_data = UpdateAlcSchema().load(data)
        if "event" in validated_data:
            event.event = validated_data["event"]
        if "notes" in validated_data:
            event.notes = data.get("notes", event.notes)
        db.session.commit()
        return jsonify(event.to_dict()), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles/<int:event_id>", methods=["DELETE"])
@jwt_required()
def delete_asset_lifecycle(event_id):
    """
    Endpoint to delete an Asset Lifecycle record by its ID.
    This endpoint requires the user to be authenticated via JWT. It deletes
    the specified asset lifecycle event from the database.
    Args:
        event_id (int): The ID of the asset lifecycle event to delete.
    Returns:
        Response: JSON object indicating success or failure
        of the delete operation.
    """
    try:
        event = db.session.get(AssetLifecycle, event_id)
        if not event:
            return jsonify({
                "error": f"Event with id {event_id} not found."
            }), 404
        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500
