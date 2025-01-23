from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import AssetTransfer, Asset
from flask_jwt_extended import jwt_required
from utils.validations.at_validate import RegATSchema

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
            "transferred_from": assettransfer_data.get("transferred_from"),
            "asset_id": assettransfer_data.get("asset_id")
        })
        assettransfer_info = schema.load(assettransfer_data)

        asset = Asset.query.get(assettransfer_info["asset_id"])

        if not asset:
            return jsonify({"error": "Asset not found"}), 404
        asset.assigned_to = assettransfer_info["transferred_to"]
        asset.location_id = assettransfer_info["to_location_id"]

        new_assettransfer = AssetTransfer(
            asset_id=assettransfer_info["asset_id"],
            from_location_id=assettransfer_info["from_location_id"],
            to_location_id=assettransfer_info["to_location_id"],
            transferred_from=assettransfer_info["transferred_from"],
            transferred_to=assettransfer_info["transferred_to"],
            notes=assettransfer_info["notes"]
        )
        db.session.add(new_assettransfer)
        db.session.commit()
        return jsonify({
            "message": "AssetTransfer registered successfully!",
            "assettransfer": {
                "asset_id": new_assettransfer.asset_id,
                "from_location_id": new_assettransfer.from_location_id,
                "to_location_id": new_assettransfer.to_location_id,
                "transferred_from": new_assettransfer.transferred_from,
                "transferred_to": new_assettransfer.transferred_to,
                "notes": new_assettransfer.notes
            }
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
