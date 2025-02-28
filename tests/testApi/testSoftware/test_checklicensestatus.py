from app.models.v1 import Software
import pytest
from app.extensions import db
from datetime import datetime, timedelta, timezone


def test_check_license_status_success(user_client, app):
    """
    Test retrieving software with expiring or expired licenses successfully
    """
    client, headers = user_client
    with app.app_context():
        software = Software(
            name="Test Software",
            version="1.0",
            license_key="TEST-1234",
            expiry_date=datetime.now(timezone.utc).date() + timedelta(days=10),
        )
        db.session.add(software)
        db.session.commit()

    response = client.get("/software/license-status?days=15", headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert len(response.json["Softwares"]) > 0


def test_check_license_status_no_expiring_licenses(user_client, app):
    """
    Test retrieving software when no licenses are
    expiring within the given days
    """
    client, headers = user_client
    with app.app_context():
        db.session.query(Software).delete()
        db.session.commit()

    response = client.get("/software/license-status?days=30", headers=headers)
    assert response.status_code == 200
    assert response.json["Softwares"] == []
    assert "licenses expiring in the next 30 days" in response.json["Message"]


def test_check_license_status_invalid_days_param(user_client):
    """Test handling of invalid 'days' query parameter"""
    client, headers = user_client
    response = client.get(
        "/software/license-status?days=invalid", headers=headers)
    assert response.status_code == 400


def test_check_license_status_default_days(user_client):
    """Test license status check with the default days parameter (30 days)"""
    client, headers = user_client
    response = client.get("/software/license-status", headers=headers)
    assert response.status_code == 200
    assert "licenses expiring in the next 30 days" in response.json["Message"]


def test_check_license_status_negative_days(user_client):
    """Test handling of a negative 'days' query parameter"""
    client, headers = user_client
    response = client.get("/software/license-status?days=-10", headers=headers)
    print(response.json)
    assert response.status_code == 400


def test_check_license_status_unauthorized(client):
    """Test retrieving software license status without JWT token"""
    response = client.get("/software/license-status")
    assert response.status_code == 401


def test_check_license_status_invalid_method(user_client):
    """
    Test accessing license status check with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/software/license-status", headers=headers)
    assert response.status_code == 405


@pytest.mark.xfail(reason="recheck on mocking")
def test_check_license_status_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during license status retrieval
    """
    client, headers = user_client
    mocker.patch(
        "app.models.v1.Software.query.get",
        side_effect=Exception("DB error"))
    response = client.get("/software/license-status", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
