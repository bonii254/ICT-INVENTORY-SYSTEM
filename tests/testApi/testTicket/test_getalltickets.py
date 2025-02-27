from app.models.v1 import User, Asset, Ticket
from app.extensions import db


def test_get_all_tickets_success(user_client, app):
    """Test retrieving all tickets successfully"""
    client, headers = user_client
    response = client.get("/tickets", headers=headers)
    assert response.status_code == 200
    assert "tickets" in response.json
    assert isinstance(response.json["tickets"], list)


def test_get_all_tickets_no_data(user_client, app):
    """Test retrieving all tickets when no tickets exist"""
    client, headers = user_client
    with app.app_context():
        db.session.query(Ticket).delete()
        db.session.commit()
    response = client.get("/tickets", headers=headers)
    assert response.status_code == 200
    assert response.json["tickets"] == []


def test_get_all_tickets_unauthorized(client):
    """Test retrieving all tickets without JWT token"""
    response = client.get("/tickets")
    assert response.status_code == 401


def test_get_all_tickets_invalid_method(user_client):
    """Test accessing all tickets with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/tickets", headers=headers)
    assert response.status_code == 405
