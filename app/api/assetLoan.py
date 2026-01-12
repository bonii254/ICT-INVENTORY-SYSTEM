from flask import Blueprint, request, jsonify
import traceback
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime
from app.extensions import db
from app.models.v1 import AssetLoan, Asset, User, ExternalMaintenance
from utils.validations.asset_loan_validate import (
    AssetLoanCreateSchema, AssetLoanUpdateSchema)


asset_loan_bp = Blueprint("asset_loan_bp", __name__)


@asset_loan_bp.route("/register/asset-loans", methods=["POST"])
@jwt_required()
def create_asset_loan():
    """Create a new asset loan."""
    try:
        data = request.get_json()
        validated = AssetLoanCreateSchema().load(data)
        current_user = db.session.get(User, get_jwt_identity())
        asset = db.session.get(Asset, validated["asset_id"])
        if not asset or asset.domain_id != current_user.domain_id:
            return jsonify({"error": "Asset not found or unauthorized."}), 404
        
        active_loan = AssetLoan.query.filter_by(
            asset_id=asset.id, status="BORROWED"
        ).first()
        if active_loan:
            return jsonify({
                "error": 
                    f"Asset '{asset.name}' is currently borrowed and not yet returned."
            }), 400
            
        active_maintenance = ExternalMaintenance.query.filter_by(
            asset_id=asset.id, status="SENT"
        ).first()
        if active_maintenance:
            return jsonify({
                "error": 
                    f"Asset '{asset.name}' is currently out for maintenance and cannot be loaned."
            }), 400

        new_loan = AssetLoan(
            asset_id=validated["asset_id"],
            borrower_id=validated["borrower_id"],
            expected_return_date=validated["expected_return_date"],
            condition_before=validated["condition_before"],
            remarks=validated.get("remarks"),
            domain_id=current_user.domain_id
        )

        db.session.add(new_loan)
        db.session.commit()
        return jsonify({
            "message": "Asset loan created successfully.",
            "loan": new_loan.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@asset_loan_bp.route("/assetloans", methods=["GET"])
@jwt_required()
def get_asset_loans():
    """Retrieve all asset loans for the current user's domain."""
    try:
        current_user = db.session.get(User, get_jwt_identity())
        loans = AssetLoan.query.filter_by(
            domain_id=current_user.domain_id).all()
        return jsonify({
            "asset_loans": [loan.to_dict() for loan in loans]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@asset_loan_bp.route("/asset-loans/<int:id>", methods=["GET"])
@jwt_required()
def get_asset_loan(id):
    """Retrieve a specific asset loan by ID."""
    try:
        current_user = db.session.get(User, get_jwt_identity())
        loan = AssetLoan.query.filter_by(
            id=id, domain_id=current_user.domain_id).first()
        if not loan:
            return jsonify({"error": "Asset loan not found"}), 404
        return jsonify(loan.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@asset_loan_bp.route("/asset-loans/<int:id>", methods=["PUT"])
@jwt_required()
def update_asset_loan(id):
    """Update asset loan details (return or remark updates)."""
    try:
        current_user = db.session.get(User, get_jwt_identity())
        loan = AssetLoan.query.filter_by(
            id=id, domain_id=current_user.domain_id).first()
        if not loan:
            return jsonify({"error": "Asset loan not found"}), 404

        data = request.get_json()
        validated = AssetLoanUpdateSchema().load(data)

        for key, value in validated.items():
            setattr(loan, key, value)

        if loan.actual_return_date or loan.condition_after:
            loan.status = "RETURNED"

        db.session.commit()
        return jsonify({
            "message": "Asset loan updated successfully.",
            "loan": loan.to_dict()
        }), 200
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@asset_loan_bp.route("/asset-loans/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_asset_loan(id):
    """Delete an asset loan."""
    try:
        current_user = db.session.get(User, get_jwt_identity())
        loan = AssetLoan.query.filter_by(
            id=id, domain_id=current_user.domain_id).first()
        if not loan:
            return jsonify({"error": "Asset loan not found"}), 404
        

        db.session.delete(loan)
        db.session.commit()
        return jsonify({"message": "Asset loan deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@asset_loan_bp.route("/asset-loans", methods=["GET"])
@jwt_required()
def list_asset_loans():
    """
    Retrieve asset loans with optional filters:
        - borrower_id: int
        - asset_id: int
        - status: SENT/RETURNED/OVERDUE
        - overdue: bool (true/false)
        - start_date, end_date: filter loans created between dates (YYYY-MM-DD)
    """
    try:
        current_user = db.session.get(User, get_jwt_identity())
        query = AssetLoan.query.filter_by(domain_id=current_user.domain_id)

        # Filters
        borrower_id = request.args.get("borrower_id", type=int)
        asset_id = request.args.get("asset_id", type=int)
        status = request.args.get("status")
        overdue = request.args.get("overdue", type=str)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if borrower_id:
            query = query.filter_by(borrower_id=borrower_id)
        if asset_id:
            query = query.filter_by(asset_id=asset_id)
        if status:
            query = query.filter_by(status=status.upper())
        if overdue and overdue.lower() == "true":
            query = query.filter(
                AssetLoan.expected_return_date < datetime.utcnow(),
                AssetLoan.actual_return_date.is_(None)
            )
        if start_date:
            query = query.filter(
                AssetLoan.loan_date >= datetime.strptime(start_date, "%Y-%m-%d"))
        if end_date:
            query = query.filter(
                AssetLoan.expected_return_date <= datetime.strptime(end_date, "%Y-%m-%d"))

        loans = query.order_by(AssetLoan.loan_date.desc()).all()

        # Convert loans to dict with nested asset and borrower info
        result = []
        for loan in loans:
            loan_dict = loan.to_dict()  
            asset = db.session.get(Asset, loan.asset_id)
            borrower = db.session.get(User, loan.borrower_id)
            loan_dict["asset"] = {
                "name": asset.name if asset else None,
                "serial_no": asset.serial_number if asset else None,
                "asset_tag": asset.fresha_tag if asset else None,
            }
            loan_dict["borrower"] = {
                "full_name": borrower.fullname if borrower else None,
                "payroll_no": borrower.payroll_no if borrower else None,
            }
            result.append(loan_dict)

        return jsonify({"asset_loans": result}), 200

    except Exception as e:
        print("Exception occurred:")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
