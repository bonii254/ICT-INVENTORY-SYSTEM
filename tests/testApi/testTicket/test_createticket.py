from app.models.v1 import User, Asset, Ticket
from app.extensions import db


def test_create_ticket_success(user_client, app):
    """Test successful ticket creation"""
    client, headers = user_client
    with app.app_context():
        asset = Asset.query.first()
        user = User.query.first()
        assert asset, "No asset found in database"
        assert user, "No user found in database"
    payload = {
        "asset_id": asset.id,
        "user_id": user.id,
        "status": "Open",
        "description": "Issue with the asset",
        "resolution_notes": "Pending resolution"
    }
    response = client.post("/register/ticket", headers=headers, json=payload)
    assert response.status_code == 201
    assert response.json["asset name"] == asset.name
    assert response.json["user name"] == user.fullname
    assert response.json["status"] == "Open"
    assert response.json["description"] == "Issue with the asset"
    assert response.json["resolution_notes"] == "Pending resolution"


def test_create_ticket_missing_fields(user_client):
    """Test ticket creation with missing required fields"""
    client, headers = user_client
    payload = {
        "asset_id": 1,
        "status": "Open",
    }
    response = client.post("/register/ticket", headers=headers, json=payload)
    assert response.status_code == 400
    assert "The 'user_id' field is required." \
        in response.json["error"]["user_id"]


def test_create_ticket_invalid_data_types(user_client):
    """Test ticket creation with invalid data types"""
    client, headers = user_client
    payload = {
        "asset_id": "invalid",
        "user_id": "invalid",
        "status": 123,
        "description": 456,
        "resolution_notes": []
    }
    response = client.post("/register/ticket", headers=headers, json=payload)
    assert response.status_code == 400
    assert "asset_id" in response.json["error"]
    assert "user_id" in response.json["error"]
    assert "status" in response.json["error"]
    assert "description" in response.json["error"]


def test_create_ticket_invalid_content_type(user_client):
    """Test ticket creation with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "asset_id": 1,
        "user_id": 2,
        "status": "open",
        "description": "Issue with asset",
        "resolution_notes": "Pending"
    }
    response = client.post("/register/ticket", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_create_ticket_unauthorized(client):
    """Test ticket creation without JWT token"""
    payload = {
        "asset_id": 1,
        "user_id": 2,
        "status": "open",
        "description": "Issue with asset",
        "resolution_notes": "Pending"
    }
    response = client.post("/register/ticket", json=payload)
    assert response.status_code == 401


def test_create_ticket_invalid_method(user_client):
    """Test accessing ticket creation with an unsupported HTTP method (GET)"""
    client, headers = user_client
    response = client.get("/register/ticket", headers=headers)
    assert response.status_code == 405


def test_create_ticket_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during ticket creation"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    payload = {
        "asset_id": 1,
        "user_id": 2,
        "status": "Open",
        "description": "Issue with asset",
        "resolution_notes": "Pending"
    }
    response = client.post("/register/ticket", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
