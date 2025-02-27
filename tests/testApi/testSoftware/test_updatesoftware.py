from app.models.v1 import Software
from app.extensions import db


def test_update_software_success(user_client, app):
    """Test successfully updating an existing software"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"

    payload = {
        "name": "Updated Software",
        "version": "2.0",
        "license_key": "UPDATED-1234-5678",
        "expiry_date": "2026-12-31"
    }
    response = client.put(
        f"/software/{software.id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["software"]["name"] == "Updated Software"
    assert response.json["software"]["version"] == "2.0"
    assert response.json["software"]["license_key"] == "UPDATED-1234-5678"
    assert response.json["software"]["expiry_date"] == \
        "Thu, 31 Dec 2026 00:00:00 GMT"


def test_update_software_not_found(user_client):
    """Test updating a non-existent software"""
    client, headers = user_client
    payload = {"name": "Non-Existent Software"}
    response = client.put("/software/99999", headers=headers, json=payload)
    assert response.status_code == 404
    assert "Software with id 99999 not found" in response.json["error"]


def test_update_software_invalid_data(user_client):
    """Test updating software with invalid data types"""
    client, headers = user_client
    payload = {
        "name": 123,
        "version": [],
        "license_key": {},
        "expiry_date": "invalid-date"
    }
    response = client.put("/software/1", headers=headers, json=payload)
    assert response.status_code == 400
    assert "name" in response.json["error"]
    assert "version" in response.json["error"]
    assert "license_key" in response.json["error"]
    assert "expiry_date" in response.json["error"]


def test_update_software_partial_update(user_client, app):
    """Test updating only some fields of software"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"

    payload = {"version": "3.5"}
    response = client.put(
        f"/software/{software.id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["software"]["version"] == "3.5"
    assert response.json["software"]["name"] == software.name


def test_update_software_invalid_content_type(user_client):
    """Test updating software with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "name": "New Software",
        "version": "1.1"
    }
    response = client.put("/software/1", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_update_software_unauthorized(client):
    """Test updating software without JWT token"""
    payload = {"name": "Unauthorized Software"}
    response = client.put("/software/1", json=payload)
    assert response.status_code == 401


def test_update_software_invalid_method(user_client):
    """Test accessing software update with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/software/1", headers=headers)
    assert response.status_code == 405


def test_update_software_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during software update"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit",
        side_effect=Exception("DB error"))
    payload = {
        "name": "Broken Software",
        "version": "5.0"
    }
    response = client.put("/software/1", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
