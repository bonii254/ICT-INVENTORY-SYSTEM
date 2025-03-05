from app.models.v1 import Alert
from app.extensions import db
import pytest


def test_get_all_alerts_success(user_client, app):
    """Test successfully retrieving all alerts"""
    client, headers = user_client
    with app.app_context():
        alert = Alert(
            consumable_id=1,
            message="Low stock alert",
            status="PENDING")
        db.session.add(alert)
        db.session.commit()
    response = client.get("/alerts", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_get_all_alerts_no_alerts(user_client):
    """Test retrieving alerts when there are no active alerts"""
    client, headers = user_client
    response = client.get("/alerts", headers=headers)
    assert response.status_code == 200
    assert response.json == []


def test_get_all_alerts_unauthorized(client):
    """Test retrieving alerts without authentication"""
    response = client.get("/alerts")
    assert response.status_code == 401


def test_get_all_alerts_invalid_method(user_client):
    """Test accessing the endpoint with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/alerts", headers=headers)
    assert response.status_code == 405


def test_get_all_alerts_internal_server_error(user_client, mocker):
    """Test handling unexpected server errors during alert retrieval"""
    client, headers = user_client
    mocker.patch.object(
       Alert, "query",
       new_callable=mocker.PropertyMock,
       side_effect=Exception("DB error"))

    response = client.get("/alerts", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
