from app.models.v1 import Software
from app.extensions import db
import pytest
from datetime import datetime, timedelta, timezone


def test_get_software_by_expiry_range_success(user_client, app):
    """
    Test successfully retrieving software records
    expiring within a given date range
    """
    client, headers = user_client
    with app.app_context():
        software = Software(
            name="Test Software",
            version="1.0",
            license_key="TEST-1234",
            expiry_date=datetime.now(timezone.utc).date() + timedelta(days=15),
        )
        db.session.add(software)
        db.session.commit()

    start_date = (
        datetime.now(timezone.utc) + timedelta(days=10)).strftime("%Y-%m-%d")
    end_date = (
        datetime.now(timezone.utc) + timedelta(days=20)).strftime("%Y-%m-%d")

    response = client.get(
        f"/software/expiry?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert len(response.json["Softwares"]) > 0


def test_get_software_by_expiry_range_no_data(user_client):
    """
    Test retrieving software records when no
    software falls within the given date range
    """
    client, headers = user_client
    start_date = "2030-01-01"
    end_date = "2030-12-31"

    response = client.get(
        f"/software/expiry?start_date={start_date}&end_date={end_date}",
        headers=headers
    )
    assert response.status_code == 200
    assert response.json["Softwares"] == []


def test_get_software_by_expiry_range_missing_dates(user_client):
    """Test handling when 'start_date' or 'end_date' is missing"""
    client, headers = user_client

    response1 = client.get(
        "/software/expiry?start_date=2025-01-01", headers=headers)
    assert response1.status_code == 400
    assert "Both 'start_date' and 'end_date' are required." \
        in response1.json["error"]
    response2 = client.get(
        "/software/expiry?end_date=2025-12-31", headers=headers)
    assert response2.status_code == 400
    assert "Both 'start_date' and 'end_date' are required." \
        in response2.json["error"]


def test_get_software_by_expiry_range_invalid_date_format(user_client):
    """Test handling of invalid date format in query parameters"""
    client, headers = user_client
    response = client.get(
        "/software/expiry?start_date=invalid&end_date=2025-12-31",
        headers=headers
    )
    assert response.status_code == 400
    assert "Invalid date format. Use YYYY-MM-DD." in response.json["error"]


def test_get_software_by_expiry_range_unauthorized(client):
    """Test retrieving software by expiry range without JWT token"""
    response = client.get(
        "/software/expiry?start_date=2025-01-01&end_date=2025-12-31")
    assert response.status_code == 401


def test_get_software_by_expiry_range_invalid_method(user_client):
    """
    Test accessing the expiry range endpoint with an
    unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/software/expiry", headers=headers)
    assert response.status_code == 405


@pytest.mark.xfail(reason="mocker failing")
def test_get_software_by_expiry_range_internal_server_error(
        user_client, mocker):
    """
    Test handling of unexpected server error during expiry range retrieval
    """
    client, headers = user_client
    mocker.patch(
        "app.models.v1.Software.query.filter",
        side_effect=Exception("DB error")
    )
    response = client.get(
        "/software/expiry?start_date=2025-01-01&end_date=2025-12-31",
        headers=headers
    )
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
