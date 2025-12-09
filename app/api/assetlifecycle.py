from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import AssetLifecycle, Asset, User
from utils.validations.alc_validate import RegAlcSchema, UpdateAlcSchema

alc_bp = Blueprint("als_bp", __name__)

def get_current_user():
    user_id = get_jwt_identity()
    return User.query.get(user_id)

@alc_bp.route("/register/assetlifecycle", methods=["POST"])
@jwt_required()
def create_alc():
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 415

        alc_data = request.get_json()
        alc_info = RegAlcSchema().load(alc_data)

        current_user = get_current_user()
        new_alc = AssetLifecycle(
            asset_id=alc_info["asset_id"],
            event=alc_info.get("event"),
            notes=alc_info.get("notes"),
            domain_id=current_user.domain_id
        )

        db.session.add(new_alc)
        db.session.commit()
        return jsonify({"message": "AssetLifecycle created successfully"}), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles", methods=["GET"])
@jwt_required()
def get_all_asset_lifecycles():
    try:
        current_user = get_current_user()
        events = AssetLifecycle.query.filter_by(
            domain_id=current_user.domain_id).all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles/<int:event_id>", methods=["GET"])
@jwt_required()
def get_asset_lifecycle(event_id):
    try:
        current_user = get_current_user()
        event = AssetLifecycle.query.filter_by(
            id=event_id, domain_id=current_user.domain_id).first()
        if not event:
            return jsonify({
                "error": 
                    f"AssetLifecycle with id {event_id} not found or access denied."}), 404
        return jsonify(event.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/assets/<int:asset_id>/lifecycles", methods=["GET"])
@jwt_required()
def get_asset_lifecycles_by_asset(asset_id):
    try:
        current_user = get_current_user()
        asset = Asset.query.get(asset_id)
        if not asset:
            return jsonify({"error": f"Asset with id {asset_id} not found."}), 404

        events = AssetLifecycle.query.filter_by(
            asset_id=asset_id, domain_id=current_user.domain_id).all()
        return jsonify([event.to_dict() for event in events]), 200
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


@alc_bp.route("/asset-lifecycles/<int:event_id>", methods=["PUT"])
@jwt_required()
def update_asset_lifecycle(event_id):
    try:
        if not request.is_json:
            return jsonify(
                {"error": "Content-Type must be application/json"}), 415

        current_user = get_current_user()
        event = AssetLifecycle.query.filter_by(
            id=event_id, domain_id=current_user.domain_id).first()
        if not event:
            return jsonify({
                "error": f"Event with id {event_id} not found or access denied."}), 404

        data = request.get_json()
        validated_data = UpdateAlcSchema().load(data)
        if "event" in validated_data:
            event.event = validated_data["event"]
        if "notes" in validated_data:
            event.notes = validated_data.get("notes", event.notes)
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
    try:
        current_user = get_current_user()
        event = AssetLifecycle.query.filter_by(
            id=event_id, domain_id=current_user.domain_id).first()
        if not event:
            return jsonify({
                "error": f"Event with id {event_id} not found or access denied."}), 404

        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "Deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500
