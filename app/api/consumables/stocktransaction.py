from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.v1 import Consumables, StockTransaction, Alert, User
from utils.validations.consumables.stock_transaction_validate import (
    StockTransactionSchema)


stocktrans_bp = Blueprint("stocktrans", __name__)


@stocktrans_bp.route("/register/stocktransaction", methods=["POST"])
@jwt_required()
def reg_stocktransaction():
    """
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        transaction_data = request.get_json()
        validated_data = StockTransactionSchema().load(transaction_data)
        user = User.query.get_or_404(int(get_jwt_identity()))
        consumable = Consumables.query.get(validated_data["consumable_id"])
        if not consumable:
            return jsonify({"error": "Consumable not found."}), 404
        transaction_type = validated_data["transaction_type"]
        quantity = validated_data["quantity"]
        if transaction_type == "IN":
            consumable.quantity += quantity
            alert = Alert.query.filter_by(
                consumable_id=consumable.id, status="PENDING").first()
            if alert and consumable.quantity >= consumable.reorder_level:
                alert.status = "RESOLVED"

        elif transaction_type == "OUT":
            if consumable.quantity < quantity:
                return jsonify({
                    "error": "Insufficient stock for this transaction."}), 400
            consumable.quantity -= quantity
            if consumable.quantity < consumable.reorder_level:
                new_alert = Alert(
                    consumable_id=consumable.id,
                    message=f"Stock for {consumable.name}" +
                    " is below reorder level.",
                    status="PENDING"
                )
                db.session.add(new_alert)
        new_transaction = StockTransaction(
            consumable_id=validated_data["consumable_id"],
            department_id=validated_data["department_id"],
            transaction_type=transaction_type,
            quantity=quantity,
            user_id=user.fullname
        )
        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({
            "message":
            "Stock transaction registered successfully.",
            "transaction": new_transaction.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
