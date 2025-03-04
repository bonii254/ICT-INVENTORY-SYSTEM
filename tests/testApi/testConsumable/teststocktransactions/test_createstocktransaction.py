from app.models.v1 import StockTransaction, Consumables, Department
from app.extensions import db


def test_register_stock_transaction_in_success(user_client, app):
    """Test successfully registering an IN stock transaction"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        dept = Department.query.first()
        con_id = consumable.id
        dept_id = dept.id
    payload = {
        "consumable_id": con_id,
        "department_id": dept_id,
        "transaction_type": "IN",
        "quantity": 10
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 201
    assert "Stock transaction registered successfully." \
        in response.json["message"]


def test_register_stock_transaction_out_success(user_client, app):
    """Test successfully registering an OUT stock transaction"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        dept = Department.query.first()
        con_id = consumable.id
        dept_id = dept.id
    payload = {
        "consumable_id": con_id,
        "department_id": dept_id,
        "transaction_type": "OUT",
        "quantity": 5
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 201


def test_register_stock_transaction_insufficient_stock(user_client, app):
    """Test stock OUT transaction when stock is insufficient"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        dept = Department.query.first()
        con_id = consumable.id
        dept_id = dept.id
    payload = {
        "consumable_id": con_id,
        "department_id": dept_id,
        "transaction_type": "OUT",
        "quantity": 99999
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 400
    assert "Insufficient stock for this transaction." in response.json["error"]


def test_register_stock_transaction_invalid_type(user_client):
    """Test registering a stock transaction with invalid transaction type"""
    client, headers = user_client
    payload = {
        "consumable_id": 1,
        "department_id": 1,
        "transaction_type": "INVALID_TYPE",
        "quantity": 10
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 400


def test_register_stock_transaction_negative_quantity(user_client):
    """Test registering a stock transaction with negative quantity"""
    client, headers = user_client
    payload = {
        "consumable_id": 1,
        "department_id": 1,
        "transaction_type": "IN",
        "quantity": -10
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 400


def test_register_stock_transaction_unauthorized(client):
    """Test registering a stock transaction without authentication"""
    payload = {
        "consumable_id": 1,
        "department_id": 1,
        "transaction_type": "IN",
        "quantity": 10
    }
    response = client.post("/register/stocktransaction", json=payload)
    assert response.status_code == 401


def test_register_stock_transaction_internal_server_error(user_client, mocker):
    """Test handling unexpected server errors"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    payload = {
        "consumable_id": 1,
        "department_id": 1,
        "transaction_type": "IN",
        "quantity": 10
    }
    response = client.post(
        "/register/stocktransaction", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
