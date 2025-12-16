from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from marshmallow import ValidationError
from app.models.v1 import Provider, User
from utils.validations.pro_validate import (ProviderCreateSchema,
                                            ProviderUpdateSchema)


provider_bp = Blueprint("providers", __name__)


@provider_bp.route("/register/provider", methods=["POST"])
@jwt_required()
def create_provider():
    """
    Create a new provider (domain-aware).
    Automatically assigns the current user's domain_id.
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        if not request.is_json:
            return jsonify({
                 "error": "Content-Type must be application/json"}), 415

        data = ProviderCreateSchema().load(request.get_json())
        data["domain_id"] = current_user.domain_id

        new_provider = Provider(**data)
        new_provider.save()

        return jsonify({
            "message": "Provider created successfully.",
            "provider": new_provider.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@provider_bp.route("/providers", methods=["GET"])
@jwt_required()
def get_all_providers():
    """
    Retrieve all providers in the user's domain.
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        providers = Provider.query.filter_by(
            domain_id=current_user.domain_id).all()
        return jsonify({
            "providers": [p.to_dict() for p in providers]   
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@provider_bp.route("/providers/<int:provider_id>", methods=["GET"])
@jwt_required()
def get_provider(provider_id):
    """
    Retrieve a specific provider by ID (domain-scoped).
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        provider = Provider.query.filter_by(
            domain_id=current_user.domain_id, id=provider_id).first()
        if not provider:
            return jsonify({"error": "Provider not found"}), 404
        return jsonify(provider.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@provider_bp.route("/providers/<int:provider_id>", methods=["PUT"])
@jwt_required()
def update_provider(provider_id):
    """
    Update a provider's details.
    Only accessible within the user's domain.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"}), 415

        current_user = db.session.get(User, get_jwt_identity())
        provider = Provider.query.filter_by(
            domain_id=current_user.domain_id, id=provider_id).first()
        if not provider:
            return jsonify({"error": "Provider not found"}), 404

        data = ProviderUpdateSchema().load(request.get_json())
        for key, value in data.items():
            setattr(provider, key, value)

        db.session.commit()
        return jsonify({
            "message": "Provider updated successfully.",
            "provider": provider.to_dict()
        }), 200

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@provider_bp.route("/providers/<int:provider_id>", methods=["DELETE"])
@jwt_required()
def delete_provider(provider_id):
    """
    Delete a provider (domain-scoped).
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        provider = Provider.query.filter_by(
            domain_id=current_user.domain_id, id=provider_id).first()
        if not provider:
            return jsonify({"error": "Provider not found"}), 404

        provider.delete()
        return jsonify({"message": "Provider deleted successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@provider_bp.route("/providers/search", methods=["GET"])
@jwt_required()
def search_providers():
    """
    Search providers by name, contact person, or provider type.
    All queries are restricted to the user's domain automatically.
    """
    try:
        name = request.args.get("name")
        contact_person = request.args.get("contact_person")
        provider_type = request.args.get("provider_type")

        query = Provider.query

        if name:
            query = query.filter(Provider.name.ilike(f"%{name}%"))
        if contact_person:
            query = query.filter(
                Provider.contact_person.ilike(f"%{contact_person}%"))
        if provider_type:
            query = query.filter(Provider.provider_type == provider_type)

        providers = query.all()
        return jsonify({
            "providers": [p.to_dict() for p in providers]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500