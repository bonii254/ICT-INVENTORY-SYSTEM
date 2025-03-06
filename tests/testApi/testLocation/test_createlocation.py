from app.models.v1 import Location
from app.extensions import db


def test_create_location_success(user_client):
    """Test successful location registration"""
    client, headers = user_client
    new_location = {"name": "MOIROAD", "address": "githunguri"}
    response = client.post(
        "/register/location", json=new_location, headers=headers)
    print(response.json)
    assert response.status_code == 201
    data = response.get_json()
    assert "message" in data
    assert data["message"] == "Location registered successfully!"
    assert data["Location"]["name"] == new_location["name"]
    assert data["Location"]["address"] == new_location["address"]


def test_create_location_missing_name(user_client):
    """Test missing `name` field"""
    client, headers = user_client
    response = client.post(
        "/register/location", json={"address": "githuguri"}, headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_location_missing_address(user_client):
    """Test missing `address` field"""
    client, headers = user_client
    response = client.post(
        "/register/location", json={"name": "No Address"}, headers=headers)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_create_location_invalid_json(user_client):
    """Test invalid JSON format"""
    client, headers = user_client
    invalid_json = '{"name": "Invalid JSON", "address": "123"}'
    response = client.post(
        "/register/location", data=invalid_json, headers=headers)
    assert response.status_code == 415
    data = response.get_json()
    assert "error" in data


def test_create_location_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    response = client.post(
        "/register/location",
        json={"name": "Error Place", "address": "123 Error Rd"},
        headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occured: DB error" in data["error"]


def test_create_location_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    response = client.post(
        "/register/location",
        json={"name": "Secure Place", "address": "789 Secure Rd"})
    assert response.status_code == 401
