from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import and_
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.v1 import (Consumables, StockTransaction,
                           Alert, User, Department)
from utils.validations.consumables.stock_transaction_validate import (
    StockTransactionSchema)


stocktrans_bp = Blueprint("stocktrans", __name__)


@stocktrans_bp.route("/register/stocktransaction", methods=["POST"])
@jwt_required()
def reg_stocktransaction():
    """
    Registers a new stock transaction (either "IN" or "OUT") for a consumable.
    Validates the incoming request data, checks if the consumable exists,
    processes the transaction (adjusting stock quantity and creating alerts if
    necessary), and stores the transaction in the database.
    Returns:
        - 201: Stock transaction successfully registered.
        - 400: Invalid or missing data, or insufficient stock for "OUT"
            transactions.
        - 415: Unsupported Media Type if the request is not JSON.
        - 500: Internal server error if an unexpected error occurs.
    """
    try:
        if not request.is_json:
            return jsonify({
                "error":
                "Unsupported Media Type: Content-Type must be application/json"
            }), 415
        transaction_data = request.get_json()
        validated_data = StockTransactionSchema().load(transaction_data)
        user = db.session.get(User, int(get_jwt_identity()))
        if not user:
            return jsonify({"error": "user not found."}), 404
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
            user_id=user.id
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


@stocktrans_bp.route("/stocktransactions", methods=["GET"])
@jwt_required()
def get_all_transactions():
    """
    Retrieves all stock transactions from the database.
    This route fetches all records from the `StockTransaction` table
    and returns them in a JSON format.
    Returns:
        - 200: List of all stock transactions.
        - 500: Internal server error if an unexpected error occurs.
    """
    try:
        transactions = StockTransaction.query.all()
        return jsonify({
            "Transactions":
            [t.to_dict() for t in transactions]
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@stocktrans_bp.route("/transaction/search", methods=["GET"])
@jwt_required()
def search_transaction():
    """
    Searches for stock transactions based on various filter criteria.
    This route allows the user to search for stock transactions by providing
    optional query parameters:
    - fullname: Filter by user's full name.
    - department_name: Filter by department name.
    - transaction_type: Filter by transaction type ("IN" or "OUT").
    - consumable_name: Filter by consumable name.
    - start_date and end_date: Filter by transaction date range.
    Pagination is supported using the `page` and `per_page` query parameters.
    Returns:
        - 200: Paginated list of matching stock transactions.
        - 400: Invalid date format in `start_date` or `end_date`.
        - 500: Internal server error if an unexpected error occurs.
    """
    try:
        fullname = request.args.get("fullname", None, type=str)
        department_name = request.args.get("department_name", None, type=str)
        transaction_type = request.args.get("transaction_type", None, type=str)
        consumable_name = request.args.get("consumable_name", None, type=str)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=10)

        query = (
            db.session.query(StockTransaction)
            .join(User, StockTransaction.user_id == User.id)
            .join(
                Consumables, StockTransaction.consumable_id == Consumables.id)
            .join(Department, StockTransaction.department_id == Department.id)
        )
        transactions = query.all()
        print(transactions)
        filters = []

        if fullname:
            filters.append(User.fullname.ilike(f"%{fullname}%"))
        if department_name:
            filters.append(Department.name.ilike(f"%{department_name}%"))
        if transaction_type:
            filters.append(
                StockTransaction.transaction_type == transaction_type)
        if consumable_name:
            filters.append(Consumables.name.ilike(f"%{consumable_name}%"))
        if start_date:
            try:
                start_date_obj = datetime.strptime(
                    start_date, "%Y-%m-%d").date()
                filters.append(StockTransaction.created_at >= start_date_obj)
            except ValueError:
                return jsonify({
                    "error": "Invalid start_date format. Use YYYY-MM-DD."
                }), 400
        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
                filters.append(StockTransaction.created_at <= end_date_obj)
            except ValueError:
                return jsonify({
                    "error": "Invalid end_date format. Use YYYY-MM-DD."}), 400
        if filters:
            query = query.filter(and_(*filters))

        transactions = query.paginate(
            page=page, per_page=per_page, error_out=False)

        response = {
            "transactions": [t.to_dict() for t in transactions.items],
            "total": transactions.total,
            "page": transactions.page,
            "per_page": transactions.per_page,
            "pages": transactions.pages
        }

        return jsonify(response), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@stocktrans_bp.route(
        "/stocktransaction/<int:transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id):
    """
    Deletes a specific stock transaction by its ID and updates the consumable
    stock and alert status accordingly.
    It checks if the transaction exists, updates the consumable's quantity,
    and adjusts any relevant alert status.
    Args:
        transaction_id (int): The ID of the stock transaction to delete.
    Returns:
        - 200: Transaction successfully deleted, consumable stock updated,
            and alert resolved if necessary.
        - 404: Transaction not found.
        - 500: Internal server error if an unexpected error occurs.
    """
    try:
        transaction = db.session.get(StockTransaction, transaction_id)
        if not transaction:
            return jsonify({"error": "Transaction not found."}), 404
        consumable = db.session.get(Consumables, transaction.consumable_id)
        if not consumable:
            return jsonify({"error": "Consumable not found."}), 404
        if transaction.transaction_type == "IN":
            consumable.quantity -= transaction.quantity
        elif transaction.transaction_type == "OUT":
            consumable.quantity += transaction.quantity
        alert = Alert.query.filter_by(
            consumable_id=consumable.id, status="PENDING").first()
        if consumable.quantity >= consumable.reorder_level and alert:
            alert.status = "RESOLVED"
        elif consumable.quantity < consumable.reorder_level and not alert:
            new_alert = Alert(
                consumable_id=consumable.id,
                message=f"Stock for {consumable.name} is below reorder level.",
                status="PENDING"
            )
            db.session.add(new_alert)
        db.session.delete(transaction)
        db.session.commit()

        return jsonify({
            "message":
            "Transaction deleted successfully, consumable stock updated."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@stocktrans_bp.route('/alerts', methods=['GET'])
@jwt_required()
def get_all_alerts():
    """
    Retrieves all active (pending) alerts.
    """
    try:
        alerts = Alert.query.all()
        return jsonify([alert.to_dict() for alert in alerts]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500


@stocktrans_bp.route('/alerts/pending', methods=['get'])
@jwt_required()
def get_pending_alerts():
    """
    Retrieves all active (pending) alerts.
    """
    try:
        alerts = Alert.query.filter_by(status="PENDING").all()
        return jsonify([alert.to_dict() for alert in alerts]), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": f"An unexpected error occurred: {str(e)}"
        }), 500
