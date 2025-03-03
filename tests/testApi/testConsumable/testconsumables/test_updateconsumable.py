from app.models.v1 import Consumables
from app.extensions import db
import pytest


def test_update_consumable_success(user_client, app):
    """Test successfully updating a consumable"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        con_id = consumable.id
    payload = {"brand": "Toshiba", "quantity": 20}
    response = client.put(f"/update/consumable/{con_id}",
                          headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "Consumable updated successfully."


def test_update_consumable_not_found(user_client):
    """Test updating a non-existent consumable"""
    client, headers = user_client
    payload = {"name": "Tonners"}
    response = client.put("/update/consumable/99",
                          headers=headers, json=payload)
    print(response.json)
    assert response.status_code == 404
    assert "Consumable with id 99 not found." in response.get_json()["error"]


def test_update_consumable_invalid_content_type(user_client):
    """Test updating a consumable with invalid Content-Type"""
    client, headers = user_client
    payload = {"name": "Invalid Content-Type"}
    response = client.put("/update/consumable/1",
                          headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_update_consumable_invalid_data_types(user_client):
    """Test updating a consumable with invalid data types"""
    client, headers = user_client
    payload = {"name": 12345, "reorder_level": "invalid_level"}
    response = client.put("/update/consumable/1",
                          headers=headers, json=payload)
    assert response.status_code == 400
    assert "name" in response.json["error"]
    assert "reorder_level" in response.json["error"]


def test_update_consumable_empty_payload(user_client):
    """Test updating a consumable with an empty payload"""
    client, headers = user_client
    response = client.put("/update/consumable/1",
                          headers=headers, json={})
    assert response.status_code == 200
    assert "Consumable updated successfully." in response.json["message"]


def test_update_consumable_unauthorized(client):
    """Test updating a consumable without authentication"""
    payload = {"name": "Unauthorized Update"}
    response = client.put("/update/consumable/1", json=payload)
    assert response.status_code == 401


def test_update_consumable_invalid_method(user_client):
    """Test accessing update endpoint with unsupported HTTP method (GET)"""
    client, headers = user_client
    response = client.get("/update/consumable/1", headers=headers)
    assert response.status_code == 405


def test_update_consumable_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during consumable update"""
    client, headers = user_client
    mocker.patch("app.extensions.db.session.commit",
                 side_effect=Exception("DB error"))
    payload = {"name": "Database Error Test"}
    response = client.put("/update/consumable/1",
                          headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occured: DB error" in response.json["error"]
