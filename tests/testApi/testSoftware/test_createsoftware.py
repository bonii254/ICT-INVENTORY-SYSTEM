from app.models.v1 import Software
from app.extensions import db


def test_create_software_success(user_client):
    """Test successful software registration"""
    client, headers = user_client
    payload = {
        "name": "Microsoft Office",
        "version": "2021",
        "license_key": "ABC123-DEF456-GHI789",
        "expiry_date": "2025-12-31"
    }
    response = client.post("/register/software", headers=headers, json=payload)
    assert response.status_code == 201
    assert response.json["message"] == "Software created successfully"
    assert response.json["Software"]["name"] == "Microsoft Office"
    assert response.json["Software"]["version"] == "2021"
    assert response.json["Software"]["license_key"] == "ABC123-DEF456-GHI789"
    assert response.json["Software"]["expiry_date"] == \
        "Wed, 31 Dec 2025 00:00:00 GMT"


def test_create_software_missing_fields(user_client):
    """Test software registration with missing non required fields"""
    client, headers = user_client
    payload = {"name": "Adobe Photoshop"}
    response = client.post("/register/software", headers=headers, json=payload)
    print(response.json)
    assert response.status_code == 201


def test_create_software_missing_required_fields(user_client):
    """Test software registration with missing required fields"""
    client, headers = user_client
    payload = {"version": "26.0"}
    response = client.post("/register/software", headers=headers, json=payload)
    assert response.status_code == 400
    assert "name" in response.json["error"]


def test_create_software_duplicate_entry(user_client, app):
    """Test registering the same software twice"""
    client, headers = user_client
    payload = {
        "name": "Zoom",
        "version": "5.10",
        "license_key": "XYZ123-ABC456-DEF789",
        "expiry_date": "2026-01-01"
    }
    response1 = client.post(
        "/register/software", headers=headers, json=payload)
    assert response1.status_code == 201
    response2 = client.post(
        "/register/software", headers=headers, json=payload)
    assert response2.status_code == 400
    assert "Software name 'Zoom' already exists." \
        in response2.json["error"]["name"]


def test_create_software_invalid_content_type(user_client):
    """Test software registration with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "name": "Microsoft Teams",
        "version": "1.4",
        "license_key": "TEAMS-1234-5678",
        "expiry_date": "2024-12-30"
    }
    response = client.post("/register/software", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_create_software_unauthorized(client):
    """Test software registration without JWT token"""
    payload = {
        "name": "Slack",
        "version": "4.15",
        "license_key": "SLACK-9876-5432",
        "expiry_date": "2026-06-01"
    }
    response = client.post("/register/software", json=payload)
    assert response.status_code == 401


def test_create_software_invalid_method(user_client):
    """
    Test accessing software registration with an unsupported HTTP method (GET)
    """
    client, headers = user_client
    response = client.get("/register/software", headers=headers)
    assert response.status_code == 405


def test_create_software_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during software registration"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit",
        side_effect=Exception("DB error"))
    payload = {
        "name": "AutoCAD",
        "version": "2023",
        "license_key": "AUTOCAD-1111-2222",
        "expiry_date": "2025-09-15"
    }
    response = client.post("/register/software", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
