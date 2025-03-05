from app.models.v1 import Alert
from app.extensions import db
import pytest


def test_get_pending_alerts_success(user_client, app):
    """Test retrieving all pending alerts successfully"""
    client, headers = user_client
    with app.app_context():
        alert1 = Alert(
            consumable_id=1, message="Low stock", status="PENDING")
        alert2 = Alert(
            consumable_id=2, message="Out of stock", status="PENDING")
        db.session.add_all([alert1, alert2])
        db.session.commit()
    response = client.get("/alerts/pending", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) >= 2


def test_get_pending_alerts_no_alerts(user_client, app):
    """Test retrieving pending alerts when none exist"""
    client, headers = user_client
    with app.app_context():
        Alert.query.filter_by(status="PENDING").delete()
        db.session.commit()
    response = client.get("/alerts/pending", headers=headers)
    assert response.status_code == 200
    assert response.json == []


def test_get_pending_alerts_unauthorized(client):
    """Test retrieving pending alerts without authentication"""
    response = client.get("/alerts/pending")
    assert response.status_code == 401
    assert "error" in response.json


def test_get_pending_alerts_invalid_method(user_client):
    """
    Test accessing the pending alerts endpoint with
    an unsupported HTTP method
    """
    client, headers = user_client
    response = client.post("/alerts/pending", headers=headers)
    assert response.status_code == 405
