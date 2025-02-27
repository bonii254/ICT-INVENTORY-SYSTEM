from app.models.v1 import User, Asset, Ticket
from app.extensions import db


def test_get_ticket_success(user_client, app):
    """Test retrieving a specific ticket successfully"""
    client, headers = user_client
    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket, "No ticket found in database"
    response = client.get(f"/ticket/{ticket.id}", headers=headers)
    assert response.status_code == 200
    assert "status" in response.json
    assert response.json["status"] == ticket.status
    assert response.json["description"] == ticket.description
    assert response.json["resolution_notes"] == ticket.resolution_notes


def test_get_ticket_not_found(user_client):
    """Test retrieving a non-existent ticket"""
    client, headers = user_client
    response = client.get("/ticket/99999", headers=headers)
    assert response.status_code == 404
    assert "Ticket with id 99999 not found." in response.json["error"]


def test_get_ticket_unauthorized(client):
    """Test retrieving a ticket without JWT token"""
    response = client.get("/ticket/1")
    assert response.status_code == 401


def test_get_ticket_invalid_id(user_client):
    """Test retrieving a ticket with an invalid ID format"""
    client, headers = user_client
    response = client.get("/ticket/invalid", headers=headers)
    assert response.status_code == 404


def test_get_ticket_invalid_method(user_client):
    """
    Test accessing ticket retrieval with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/ticket/1", headers=headers)
    assert response.status_code == 405


def test_get_ticket_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during ticket retrieval"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB error"))
    response = client.get("/ticket/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
