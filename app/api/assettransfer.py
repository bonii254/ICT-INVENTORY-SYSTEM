from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import AssetTransfer, Asset, User
from flask_jwt_extended import jwt_required
from utils.validations.at_validate import RegATSchema, UpdateATSchema

at_bp = Blueprint("at_bp", __name__)


@at_bp.route('/register/assettransfer', methods=['POST'])
@jwt_required()
def create_assettransfer():
    """
    Create AssetTransfer
    POST /assettransfer/register
    Creates a new transfer record for an asset.

    Request Body (JSON):
      - asset_id (int, required): ID of the asset.
      - from_location_id (int, optional): ID of the originating location.
      - to_location_id (int, optional): ID of the destination location.
      - transferred_from (int, optional): ID of the user initiating the
      transfer.
      - transferred_to (int, optional): ID of the receiving user.
      - notes (str, optional): Transfer details.

    Responses:
      201: AssetTransfer created successfully.
      400: Validation errors in the request.
      415: Content-Type must be application/json.
      500: Internal server error.

    Security:
      JWT required.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type. Content-Type" +
                    " must be application/json."
            }), 415
        assettransfer_data = request.get_json()
        schema = RegATSchema(context={
            "asset_id": assettransfer_data.get("asset_id")
        })
        assettransfer_info = schema.load(assettransfer_data)

        asset = db.session.get(Asset, assettransfer_info["asset_id"])

        if not asset:
            return jsonify({"error": "Asset not found"}), 404

        new_assettransfer = AssetTransfer(
            asset_id=assettransfer_info["asset_id"],
            from_location_id=asset.location_id,
            to_location_id=assettransfer_info["to_location_id"],
            transferred_from=asset.assigned_to,
            transferred_to=assettransfer_info["transferred_to"],
            notes=assettransfer_info["notes"]
        )
        asset.assigned_to = assettransfer_info["transferred_to"]
        asset.location_id = assettransfer_info["to_location_id"]
        db.session.add(new_assettransfer)
        db.session.commit()
        return jsonify({
            "message": "AssetTransfer registered successfully!",
            "assettransfer": new_assettransfer.to_dict()
        }), 201
    except ValidationError as err:
        return jsonify({
            "errors": err.messages
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected erroroccured: {str(e)}"
        }), 500


@at_bp.route('/assettransfers', methods=['GET'])
@jwt_required()
def get_all_asset_transfers():
    """
    Retrieve all asset transfers.
    GET /assettransfer
    Returns:
        - 200: List of all asset transfers.
        - 500: Internal server error.
    Security:
        JWT required.
    """
    try:
        asset_transfers = AssetTransfer.query.all()
        asset_transfer_list = [
            transfer.to_dict() for transfer in asset_transfers
        ]

        return jsonify({"asset_transfers": asset_transfer_list}), 200
    except Exception as e:
        return jsonify(
            {"error": f"An unexpected error occurred: {str(e)}"}
        ), 500


@at_bp.route('/assettransfer/<int:id>', methods=['GET'])
@jwt_required()
def get_asset_transfer(id):
    """
    Retrieve details of a specific asset transfer.
    GET /assettransfer/<id>
    Args:
        id (int): The ID of the asset transfer.
    Returns:
        - 200: Asset transfer details.
        - 404: Asset transfer not found.
        - 500: Internal server error.
    Security:
        JWT required.
    """
    try:
        asset_transfer = db.session.get(AssetTransfer, id)
        if not asset_transfer:
            return jsonify({"error": "Asset transfer not found"}), 404
        return jsonify(asset_transfer.to_dict()), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@at_bp.route('/assettransfer/<int:id>', methods=['PUT'])
@jwt_required()
def update_asset_transfer(id):
    """
    Update an existing asset transfer.
    PUT /assettransfer/<id>
    Args:
        id (int): The ID of the asset transfer.
    Request Body (JSON):
        - to_location_id (int, optional): New destination location.
        - transferred_to (int, optional): New receiving user.
        - notes (str, optional): Updated transfer details.
    Returns:
        - 200: Successfully updated asset transfer.
        - 400: Validation errors in request.
        - 404: Asset transfer not found.
        - 500: Internal server error.
    Security:
        JWT required.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type. Content-Type" +
                    " must be application/json."
            }), 415
        asset_transfer = db.session.get(AssetTransfer, id)
        if not asset_transfer:
            return jsonify({"error": "Asset transfer not found"}), 404

        assettransfer_data = request.get_json()
        schema = UpdateATSchema(context={
            "transferred_from": assettransfer_data.get("transferred_from"),
            "asset_id": assettransfer_data.get("asset_id")
        })
        try:
            assettransfer_info = schema.load(assettransfer_data)
        except ValidationError as err:
            return jsonify({"errors": err.messages}), 400
        if 'asset_id' in assettransfer_info:
            asset_transfer.asset_id = assettransfer_info['asset_id']
            asset = db.session.get(Asset, assettransfer_info["asset_id"])
            asset_transfer.from_location_id = asset.location_id

        if 'to_location_id' in assettransfer_info:
            asset_transfer.to_location_id = assettransfer_info[
                'to_location_id']
        if 'transferred_to' in assettransfer_info:
            asset_transfer.transferred_to = assettransfer_info[
                'transferred_to']
        if 'notes' in assettransfer_info:
            asset_transfer.notes = assettransfer_info['notes']

        db.session.commit()

        return jsonify({
            "message":
            "Asset transfer updated successfully", "asset_transfer":
            asset_transfer.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500


@at_bp.route('/assettransfer/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asset_transfer(id):
    """
    Delete an asset transfer record.
    DELETE /assettransfer/<id>
    Args:
        id (int): The ID of the asset transfer.
    Returns:
        - 200: Successfully deleted asset transfer.
        - 404: Asset transfer not found.
        - 500: Internal server error.
    Security:
        JWT required.
    """
    try:
        asset_transfer = db.session.get(AssetTransfer, id)
        if not asset_transfer:
            return jsonify({"error": "Asset transfer not found"}), 404
        db.session.delete(asset_transfer)
        db.session.commit()
        return jsonify({"message": "Asset transfer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
            f"An unexpected error occurred: {str(e)}"
        }), 500


@at_bp.route('/assettransfer/search', methods=['GET'])
@jwt_required()
def search_asset_transfers():
    """
    Search for asset transfers based on multiple filters.
    GET /assettransfer/search
    Query Parameters:
        - asset_id (int, optional): Filter by asset ID.
        - transferred_from (int, optional): Filter by sender user ID.
        - transferred_to (int, optional): Filter by recipient user ID.
        - from_location_id (int, optional): Filter by origin location.
        - to_location_id (int, optional): Filter by destination location.
    Returns:
        - 200: Matching asset transfers.
        - 500: Internal server error.
    Security:
        JWT required.
    """
    try:
        asset_id = request.args.get('asset_id', None)
        transferred_from = request.args.get('transferred_from', None)
        transferred_to = request.args.get('transferred_to', None)
        from_location_id = request.args.get('from_location_id', None)
        to_location_id = request.args.get('to_location_id', None)
        query = AssetTransfer.query
        if asset_id:
            query = query.filter(AssetTransfer.asset_id == asset_id)
        if transferred_from:
            query = query.filter(
                AssetTransfer.transferred_from == transferred_from)
        if transferred_to:
            query = query.filter(
                AssetTransfer.transferred_to == transferred_to)
        if from_location_id:
            query = query.filter(
                AssetTransfer.from_location_id == from_location_id)
        if to_location_id:
            query = query.filter(
                AssetTransfer.to_location_id == to_location_id)

        asset_transfers = query.all()

        return jsonify({"asset_transfers": [
            transfer.to_dict() for transfer in asset_transfers]}), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"}), 500
