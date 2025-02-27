from app.models.v1 import User, Asset, Ticket
from app.extensions import db


def test_update_ticket_success(user_client, app):
    """Test successful ticket update"""
    client, headers = user_client
    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket, "No ticket found in database"

    payload = {
        "status": "Closed",
        "description": "Issue resolved",
        "resolution_notes": "Replaced hardware"
    }
    response = client.put(
        f"/ticket/{ticket.id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["message"] == "Ticket updated successfully"
    assert response.json["ticket"]["description"] == "Issue resolved"
    assert response.json["ticket"]["resolution_notes"] == "Replaced hardware"


def test_update_ticket_not_found(user_client):
    """Test updating a non-existent ticket"""
    client, headers = user_client
    payload = {"status": "Closed"}
    response = client.put("/ticket/99999", headers=headers, json=payload)
    assert response.status_code == 404
    assert "Ticket with ID 99999 not found." in response.json["error"]


def test_update_ticket_invalid_data(user_client):
    """Test updating a ticket with invalid data types"""
    client, headers = user_client
    payload = {
        "status": 123,
        "description": 456,
        "resolution_notes": []
    }
    response = client.put("/ticket/1", headers=headers, json=payload)
    assert response.status_code == 400
    assert "status" in response.json["error"]
    assert "description" in response.json["error"]


def test_update_ticket_partial_update(user_client, app):
    """Test updating only some fields of a ticket"""
    client, headers = user_client
    with app.app_context():
        ticket = Ticket.query.first()
        assert ticket, "No ticket found in database"
        ticket.asset.name
        ticket.user.fullname
    payload = {
        "status": "In Progress"
    }
    response = client.put(
        f"/ticket/{ticket.id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["ticket"]["description"] == ticket.description
    assert response.json["ticket"]["resolution_notes"] == \
        ticket.resolution_notes
    assert response.json["ticket"]["asset name"] == ticket.asset.name
    assert response.json["ticket"]["status"] == "In Progress"


def test_update_ticket_invalid_content_type(user_client):
    """Test updating a ticket with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "status": "Closed",
        "description": "Issue resolved"
    }
    response = client.put("/ticket/1", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_update_ticket_unauthorized(client):
    """Test updating a ticket without JWT token"""
    payload = {
        "status": "Closed",
        "description": "Issue resolved"
    }
    response = client.put("/ticket/1", json=payload)
    assert response.status_code == 401


def test_update_ticket_invalid_method(user_client):
    """Test accessing ticket update with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/ticket/1", headers=headers)
    assert response.status_code == 405


def test_update_ticket_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during ticket update"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    payload = {
        "status": "Closed",
        "description": "Issue resolved"
    }
    response = client.put("/ticket/1", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
