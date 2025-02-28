from app.models.v1 import Software
from app.extensions import db
import pytest
from datetime import datetime, timedelta, timezone


def test_bulk_register_software_success(user_client):
    """Test successfully registering multiple software records"""
    client, headers = user_client
    payload = [
        {
            "name": "Adobe Photoshop",
            "version": "2023",
            "license_key": "PHOTOSHOP-12345",
            "expiry_date": "2025-10-15"
        },
        {
            "name": "Microsoft Office",
            "version": "2021",
            "license_key": "OFFICE-67890",
            "expiry_date": "2026-12-31"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 201
    assert "All software records created successfully" \
        in response.json["message"]


def test_bulk_register_software_missing_optional_fields(user_client):
    """Test bulk registration with some missing non-required fields"""
    client, headers = user_client
    payload = [
        {
            "name": "Slack",
            "version": "4.20",
        },
        {
            "name": "Zoom",
            "version": "5.12"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 201


def test_bulk_register_software_missing_required_fields(user_client):
    """Test bulk registration with missing required fields"""
    client, headers = user_client
    payload = [
        {
            "version": "26.0"
        },
        {
            "license_key": "INVALID-KEY"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 400
    assert "Missing data for required field." \
        in response.json["error"]["0"]["name"]


def test_bulk_register_software_duplicate_entries(user_client, app):
    """Test bulk registration with duplicate software records"""
    client, headers = user_client
    payload = [
        {
            "name": "AutoCAD",
            "version": "2023",
            "license_key": "AUTOCAD-1111-2222",
            "expiry_date": "2025-09-15"
        },
        {
            "name": "AutoCAD",
            "version": "2023",
            "license_key": "AUTOCAD-1111-2222",
            "expiry_date": "2025-09-15"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 400
    assert "Duplicate entry for 'AutoCAD' in request payload." \
        in response.json["error"]


def test_bulk_register_software_invalid_data_types(user_client):
    """Test bulk registration with incorrect data types"""
    client, headers = user_client
    payload = [
        {
            "name": "Invalid Software",
            "version": 123,
            "license_key": ["KEY-ARRAY"],
            "expiry_date": "INVALID-DATE"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 400
    assert "expiry_date" in response.json["error"]["0"]


def test_bulk_register_software_invalid_content_type(user_client):
    """Test bulk registration with invalid Content-Type"""
    client, headers = user_client
    payload = [
        {
            "name": "Google Chrome",
            "version": "100",
            "license_key": "CHROME-1234",
            "expiry_date": "2026-06-30"
        }
    ]
    response = client.post(
        "/software/bulk-register",
        headers={**headers, "Content-Type": "text/plain"},
        json=payload)
    print(response.json)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_bulk_register_software_unauthorized(client):
    """Test bulk registration without JWT token"""
    payload = [
        {
            "name": "Firefox",
            "version": "95.0",
            "license_key": "FIREFOX-9876",
            "expiry_date": "2027-03-15"
        }
    ]
    response = client.post("/software/bulk-register", json=payload)
    assert response.status_code == 401


def test_bulk_register_software_invalid_method(user_client):
    """
    Test accessing bulk registration with an unsupported HTTP method (GET)
    """
    client, headers = user_client
    response = client.get("/software/bulk-register", headers=headers)
    assert response.status_code == 405


def test_bulk_register_software_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during bulk software registration
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit",
        side_effect=Exception("DB error"))
    payload = [
        {
            "name": "Test Software",
            "version": "1.0",
            "license_key": "TEST-1234",
            "expiry_date": "2028-12-31"
        }
    ]
    response = client.post(
        "/software/bulk-register", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
