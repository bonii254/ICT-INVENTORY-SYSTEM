from app.models.v1 import Ticket
from app.extensions import db


def test_delete_ticket_success(user_client, app):
    """Test successfully deleting an existing ticket"""
    client, headers = user_client
    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket, "No ticket found in database"

    response = client.delete(f"/ticket/{ticket.id}", headers=headers)
    assert response.status_code == 201
    assert response.json["message"] == "Ticket deleted successfully."
    response_check = client.get(f"/ticket/{ticket.id}", headers=headers)
    assert response_check.status_code == 404


def test_delete_ticket_not_found(user_client):
    """Test deleting a non-existent ticket"""
    client, headers = user_client
    response = client.delete("/ticket/99999", headers=headers)
    assert response.status_code == 404
    assert response.json["error"] == "Ticket with id 99999 not found."


def test_delete_ticket_unauthorized(client):
    """Test deleting a ticket without JWT token"""
    response = client.delete("/ticket/1")
    assert response.status_code == 401


def test_delete_ticket_invalid_method(user_client):
    """Test accessing ticket deletion with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/ticket/1", headers=headers)
    assert response.status_code == 405


def test_delete_ticket_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during ticket deletion"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error")
    )
    response = client.delete("/ticket/1", headers=headers)
    assert response.status_code == 500
    assert "Unexpected error occurred" in response.json["error"]
