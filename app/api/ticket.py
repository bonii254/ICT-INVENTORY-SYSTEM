from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Ticket, User, Asset
from utils.validations.ticket_validate import RegTicSchema


tic_bp = Blueprint("tic_bp", __name__)


@tic_bp.route("/register/ticket", methods=["POST"])
@jwt_required()
def create_ticket():
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        ticket_data = request.get_json()
        ticket_info = RegTicSchema().load(ticket_data)
        new_ticket = Ticket(
            asset_id=ticket_info["asset_id"],
            user_id=ticket_info["user_id"],
            status=ticket_info["status"],
            description=ticket_info["description"],
            resolution_notes=ticket_info["resolution_notes"]
        )
        db.session.add(new_ticket)
        db.session.commit()
        asset = Asset.query.get(ticket_info["asset_id"])
        user = User.query.get(ticket_info["user_id"])
        return jsonify({
            "asset name": asset.name,
            "user name": user.fullname,
            "status": new_ticket.status,
            "description": new_ticket.description,
            "resolution_notes": new_ticket.resolution_notes
        }), 201
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error":
            f"An unexpected error occurred: {str(e)}"
        }), 500
