from app.models.v1 import StockTransaction
from app.extensions import db


def test_get_all_transactions_success(user_client, app):
    """Test successfully retrieving all stock transactions"""
    client, headers = user_client
    with app.app_context():
        transactions = StockTransaction.query.all()
        assert transactions is not None

    response = client.get("/stocktransactions", headers=headers)
    assert response.status_code == 200
    assert "Transactions" in response.json
    assert isinstance(response.json["Transactions"], list)


def test_get_all_transactions_no_records(user_client, app):
    """Test retrieving transactions when no records exist"""
    client, headers = user_client
    with app.app_context():
        db.session.query(StockTransaction).delete()
        db.session.commit()

    response = client.get("/stocktransactions", headers=headers)
    assert response.status_code == 200
    assert response.json["Transactions"] == []


def test_get_all_transactions_unauthorized(client):
    """Test retrieving stock transactions without authentication"""
    response = client.get("/stocktransactions")
    assert response.status_code == 401


def test_get_all_transactions_invalid_method(user_client):
    """Test accessing the endpoint with unsupported HTTP methods"""
    client, headers = user_client
    response = client.post("/stocktransactions", headers=headers)
    assert response.status_code == 405


def test_get_all_transactions_internal_server_error(user_client, mocker):
    """Test handling of unexpected server errors"""
    client, headers = user_client
    mocker.patch.object(
       StockTransaction, "query",
       new_callable=mocker.PropertyMock,
       side_effect=Exception("DB error"))

    response = client.get("/stocktransactions", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
