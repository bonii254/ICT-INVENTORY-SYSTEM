from app.models.v1 import Location
from app.extensions import db


def test_get_location_success(user_client):
    """Test retrieving an existing location"""
    client, headers = user_client
    location = Location.query.first()
    response = client.get(f"/location/{location.id}", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "location" in data
    assert data["location"]["name"] == location.name
    assert data["location"]["address"] == location.address


def test_get_location_not_found(user_client):
    """Test retrieving a non-existent location"""
    client, headers = user_client
    response = client.get("/location/9999", headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert "Location with id 9999 not found" in data["error"]


def test_get_location_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    location = Location.query.first()
    response = client.get(f"/location/{location.id}")
    assert response.status_code == 401


def test_get_location_invalid_id(user_client):
    """Test invalid location ID (non-integer)"""
    client, headers = user_client
    response = client.get("/location/invalid_id", headers=headers)
    assert response.status_code == 404


def test_get_location_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB error"))
    response = client.get("/location/1", headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occurred: DB error" in data["error"]
