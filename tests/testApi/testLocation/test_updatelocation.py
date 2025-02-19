from app.models.v1 import Location
from app.extensions import db


def test_update_location_success(user_client):
    """Test successful location update"""
    client, headers = user_client
    updated_data = {"name": "kenya", "address": "kiambu"}
    location = Location.query.first()
    response = client.put(
        f"/location/{location.id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "Message" in data
    assert data["Message"] == "Location updated successfully"
    assert data["location"]["name"] == updated_data["name"]
    assert data["location"]["address"] == updated_data["address"]


def test_update_location_not_found(user_client):
    """Test updating a non-existent location"""
    client, headers = user_client
    updated_data = {"name": "Does Not Exist"}
    response = client.put(
        "/location/9999", json=updated_data, headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "location with ID 9999 not found." in data["error"]


def test_update_location_missing_name(user_client):
    """Test updating location without `name` field (only `address` updated)"""
    client, headers = user_client
    location = Location.query.first()
    response = client.put(
        f"/location/{location.id}",
        json={"address": "New Address"}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["location"]["address"] == "New Address"
    assert data["location"]["name"] == location.name


def test_update_location_missing_address(user_client):
    """Test updating location without `address` field (only `name` updated)"""
    client, headers = user_client
    location = Location.query.first()
    response = client.put(
        f"/location/{location.id}",
        json={"name": "New Name"}, headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["location"]["name"] == "New Name"
    assert data["location"]["address"] == location.address


def test_update_location_invalid_json(user_client):
    """Test invalid JSON format"""
    client, headers = user_client
    location = Location.query.first()
    invalid_json = '{"name": "Invalid JSON", "address": "123"}'
    response = client.put(
        f"/location/{location.id}", data=invalid_json, headers=headers)
    assert response.status_code == 415
    data = response.get_json()
    assert "error" in data


def test_update_location_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    location = Location.query.first()
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    response = client.put(
        f"/location/{location.id}",
        json={"name": "Error Place"}, headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occurred: DB error" in data["error"]


def test_update_location_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    location = Location.query.first()
    response = client.put(
        f"/location/{location.id}",
        json={"name": "Secure Place", "address": "789 Secure Rd"})
    assert response.status_code == 401


def test_update_location_invalid_id(user_client):
    """Test invalid location ID (non-integer)"""
    client, headers = user_client
    location = Location.query.first()
    response = client.put(
        "/location/invalid_id",
        json={"name": "Invalid ID"}, headers=headers)
    assert response.status_code == 404
