from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.extensions import db
from app.models.v1 import Ticket, User, Asset
from utils.validations.ticket_validate import RegTicSchema, UpdateTicSchema


tic_bp = Blueprint("tic_bp", __name__)


@tic_bp.route("/register/ticket", methods=["POST"])
@jwt_required()
def create_ticket():
    """
    Create a new ticket.
    This endpoint allows authenticated users to create a new ticket.
    The request payload must be in JSON format and include the following
    fields:
        - asset_id: The ID of the asset associated with the ticket.
        - user_id: The ID of the user creating the ticket.
        - status: The status of the ticket (e.g., 'open', 'closed').
        - description: A description of the ticket issue.
        - resolution_notes: Notes regarding the resolution of the ticket.

    Returns:
        - 201: Ticket successfully created, along with ticket details.
        - 400: Validation errors in the request data.
        - 415: Unsupported Media Type (if Content-Type is not application/json)
        - 500: Unexpected server error.
    """
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
        asset = db.session.get(Asset, ticket_info["asset_id"])
        user = db.session.get(User, ticket_info["user_id"])
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


@tic_bp.route('/ticket/<int:ticket_id>', methods=["PUT"])
@jwt_required()
def update_ticket(ticket_id):
    """
    Update an existing ticket.
    This endpoint allows authenticated users to update the details of a
    specific ticket. The ticket is identified by its ID in the URL.
    The request payload must be in JSON format and may include any of the
    following fields:
        - asset_id: The new asset ID for the ticket.
        - user_id: The new user ID for the ticket.
        - status: The updated status of the ticket.
        - description: Updated ticket description.
        - resolution_notes: Updated resolution notes.

    Returns:
        - 200: Ticket successfully updated, along with updated ticket details.
        - 400: Validation errors in the request data.
        - 404: Ticket with the given ID not found.
        - 415: Unsupported Media Type (if Content-Type is not application/json)
        - 500: Unexpected server error.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type." +
                    " Content-Type must be application/json."
            }), 415
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            return jsonify({
                "error": f"Ticket with ID {ticket_id} not found."
            }), 404
        ticket_data = request.get_json()
        validated_ticket_data = UpdateTicSchema().load(ticket_data)
        if 'asset_id' in validated_ticket_data:
            ticket.asset_id = validated_ticket_data['asset_id']
        if 'user_id' in validated_ticket_data:
            ticket.user_id = validated_ticket_data['user_id']
        if 'status' in validated_ticket_data:
            ticket.status = validated_ticket_data['status']
        if 'description' in validated_ticket_data:
            ticket.description = validated_ticket_data['description']
        if 'resolution_notes' in validated_ticket_data:
            ticket.resolution_notes = validated_ticket_data['resolution_notes']
        db.session.commit()
        asset = db.session.get(Asset, ticket.asset_id)
        user = db.session.get(User, ticket.user_id)
        return jsonify({
            "message": "Ticket updated successfully",
            "ticket": {
                "asset name": asset.name,
                "user name": user.fullname,
                "description": ticket.description,
                "status": ticket.status,
                "resolution_notes": ticket.resolution_notes
            }
        }), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@tic_bp.route('/ticket/<int:ticket_id>', methods=["GET"])
@jwt_required()
def get_ticket(ticket_id):
    """
    Retrieve a specific ticket.
    This endpoint allows authenticated users to retrieve the details of a
    ticket by its ID. It returns information about the associated asset, user,
    and the ticket's status, description, and resolution notes.
    Returns:
        - 200: Ticket successfully retrieved.
        - 404: Ticket with the given ID not found.
        - 500: Unexpected server error.
    """
    try:
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            return jsonify({
                "error":
                f"Ticket with id {ticket_id} not found."
            }), 404
        asset = db.session.get(Asset, ticket.asset_id)
        user = db.session.get(User, ticket.user_id)
        return jsonify({
            "asset name": asset.name,
            "user name": user.fullname,
            "status": ticket.status,
            "description": ticket.description,
            "resolution_notes": ticket.resolution_notes
        })
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@tic_bp.route('/tickets/<int:asset_id>', methods=["GET"])
@jwt_required()
def get_asset_tickets(asset_id):
    """
    Retrieve all tickets for a specific asset.
    This endpoint allows authenticated users to fetch all tickets associated
    with a specific asset. The asset is identified by its ID. Each ticket
    includes the asset name, user details, status, description, and resolution
    notes.
    Returns:
        - 200: List of tickets associated with the asset.
        - 404: Asset with the given ID not found.
        - 500: Unexpected server error.
    """
    try:
        asset = db.session.get(Asset, asset_id)
        if not asset:
            return jsonify({
                "error":
                f"Asset with id {asset_id} not found."
            }), 404
        asset_name = asset.name if asset else 'unknown asset'
        tickets = db.session.query(Ticket).filter_by(asset_id=asset_id).all()
        ticket_list = [
            {
                "asset name": asset_name,
                "user name": (db.session.get(User, ticket.user_id)).fullname,
                "status": ticket.status,
                "description": ticket.description,
                "resolution_notes": ticket.resolution_notes
            } for ticket in tickets
        ]
        return jsonify({
            f"{asset_name}": ticket_list
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@tic_bp.route('/tickets', methods=["GET"])
@jwt_required()
def get_all_tickets():
    """
    Retrieve all tickets.
    This endpoint allows authenticated users to fetch all tickets in the
    system. Each ticket includes details about the associated asset, user,
    status, description, and resolution notes.
    Returns:
        - 200: List of all tickets.
        - 500: Unexpected server error.
    """
    try:
        tickets = Ticket.query.all()
        ticket_list = [
            {
                "asset name": (db.session.get(Asset, ticket.asset_id)).name,
                "user name": (db.session.get(User, ticket.user_id)).fullname,
                "status": ticket.status,
                "description": ticket.description,
                "resolution_notes": ticket.resolution_notes
            } for ticket in tickets
        ]
        return jsonify({
            "tickets": ticket_list
        }), 200
    except Exception as e:
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        })


@tic_bp.route('/ticket/<int:ticket_id>', methods=["DELETE"])
@jwt_required()
def delete_ticket(ticket_id):
    """
    Delete a specific ticket.
    This endpoint allows authenticated users to delete a ticket by its ID.
    If the ticket does not exist, an error is returned.
    Returns:
        - 201: Ticket successfully deleted.
        - 404: Ticket with the given ID not found.
        - 500: Unexpected server error.
    """
    try:
        ticket = db.session.get(Ticket, ticket_id)
        if not ticket:
            return jsonify({
                "error":
                f"Ticket with id {ticket_id} not found."
            }), 404
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({
            "message": "Ticket deleted successfully."
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Unexpected error occurred: {str(e)}"
        }), 500
