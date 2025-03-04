from app.models.v1 import Consumables
from app.extensions import db


def test_get_consumable_success(user_client, app):
    """Test successfully retrieving a consumable by ID"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        con_id = consumable.id
    response = client.get(f"/consumable/{con_id}", headers=headers)
    assert response.status_code == 200
    assert "name" in response.json
    assert "category" in response.json


def test_get_consumable_not_found(user_client):
    """Test retrieving a non-existent consumable"""
    client, headers = user_client
    response = client.get("/consumable/99", headers=headers)
    assert response.status_code == 404
    assert "Consumable with id 99 not found." in response.json["error"]


def test_get_consumable_unauthorized(client):
    """Test retrieving a consumable without authentication"""
    response = client.get("/consumable/1")
    assert response.status_code == 401


def test_get_consumable_invalid_method(user_client):
    """Test accessing the endpoint with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/consumable/1", headers=headers)
    assert response.status_code == 405


def test_get_consumable_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during retrieval"""
    client, headers = user_client
    mocker.patch("app.extensions.db.session.get",
                 side_effect=Exception("DB error"))
    response = client.get("/consumable/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occured: DB error" in response.json["error"]
