from app.models.v1 import StockTransaction, Consumables, Alert
from app.extensions import db
import pytest


def test_delete_transaction_in_success(user_client, app):
    """Test successfully deleting an 'IN' stock transaction"""
    client, headers = user_client
    with app.app_context():
        transaction = StockTransaction.query.filter_by(
            transaction_type="IN").first()
        transaction_id = transaction.id
        consumable_id = transaction.consumable.id
        initial_quantity = transaction.consumable.quantity
        transaction_quantity = transaction.quantity
    response = client.delete(
        f"/stocktransaction/{transaction_id}", headers=headers)
    assert response.status_code == 200
    assert "Transaction deleted successfully" in response.json["message"]
    with app.app_context():
        updated_quantity = db.session.get(Consumables, consumable_id).quantity
        assert updated_quantity == initial_quantity - transaction_quantity


def test_delete_transaction_resolve_alert(user_client, app):
    """
    Test that deleting an 'OUT' transaction resolves
    an alert if stock goes above reorder level
    """
    client, headers = user_client
    with app.app_context():
        transaction = StockTransaction.query.filter_by(
            transaction_type="OUT").first()
        transaction_id = transaction.id
        consumable = transaction.consumable
        alert = Alert.query.filter_by(
            consumable_id=consumable.id, status="PENDING").first()
    response = client.delete(
        f"/stocktransaction/{transaction_id}", headers=headers)
    assert response.status_code == 200
    with app.app_context():
        updated_alert = Alert.query.filter_by(
            consumable_id=consumable.id).first()
        if updated_alert:
            assert updated_alert.status == "RESOLVED"


def test_delete_transaction_create_alert(user_client, app):
    """
    Test that deleting an 'IN' transaction creates a new 'PENDING' alert
    if stock falls below reorder level
    """
    client, headers = user_client
    with app.app_context():
        transaction = StockTransaction.query.filter_by(
            transaction_type="IN").first()
        transaction_id = transaction.id
        consumable = transaction.consumable
        Alert.query.filter_by(consumable_id=consumable.id).delete()
    response = client.delete(
        f"/stocktransaction/{transaction_id}", headers=headers)
    assert response.status_code == 200
    with app.app_context():
        new_alert = Alert.query.filter_by(
            consumable_id=consumable.id, status="PENDING").first()
        assert new_alert is not None


def test_delete_transaction_resolve_alert(user_client, app):
    """
    Test that deleting an 'OUT' transaction resolves
    an alert if stock goes above reorder level
    """
    client, headers = user_client
    with app.app_context():
        transaction = StockTransaction.query.filter_by(
            transaction_type="OUT").first()
        transaction_id = transaction.id
        consumable = transaction.consumable
        alert = Alert.query.filter_by(
            consumable_id=consumable.id, status="PENDING").first()
    response = client.delete(
        f"/stocktransaction/{transaction_id}", headers=headers)
    assert response.status_code == 200
    with app.app_context():
        updated_alert = Alert.query.filter_by(
            consumable_id=consumable.id).first()
        if updated_alert:
            assert updated_alert.status == "RESOLVED"


def test_delete_transaction_not_found(user_client):
    """Test deleting a non-existent transaction (should return 404)"""
    client, headers = user_client
    response = client.delete("/stocktransaction/99999", headers=headers)
    assert response.status_code == 404
    assert "Transaction not found" in response.json["error"]


def test_delete_transaction_no_consumable(user_client, app):
    """
    Test deleting a transaction when the associated
    consumable does not exist (should return 404)
    """
    client, headers = user_client
    with app.app_context():
        transaction = StockTransaction.query.first()
        transaction_id = transaction.id
        db.session.delete(transaction.consumable)
        db.session.commit()
    response = client.delete(
        f"/stocktransaction/{transaction_id}", headers=headers)
    assert response.status_code == 404
    assert "Transaction not found." in response.json["error"]


def test_delete_transaction_unauthorized(client):
    """
    Test deleting a stock transaction without
    authentication (should return 401)
    """
    response = client.delete("/stocktransaction/1")
    assert response.status_code == 401


def test_delete_transaction_invalid_method(user_client):
    """
    Test sending an unsupported HTTP method (POST)
    to the delete transaction endpoint
    """
    client, headers = user_client
    response = client.post("/stocktransaction/1", headers=headers)
    assert response.status_code == 405


def test_delete_transaction_internal_server_error(user_client, mocker):
    """Test handling unexpected server errors"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    response = client.delete("/stocktransaction/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
