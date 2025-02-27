from app.models.v1 import User, Asset, Ticket
from app.extensions import db
import pytest


def test_get_asset_tickets_success(user_client, app):
    """Test retrieving all tickets for a specific asset successfully"""
    client, headers = user_client
    with app.app_context():
        asset = Asset.query.first()
        assert asset, "No asset found in database"
    response = client.get(f"/tickets/{asset.id}", headers=headers)
    assert response.status_code == 200
    assert asset.name in response.json
    assert isinstance(response.json[asset.name], list)


def test_get_asset_tickets_not_found(user_client):
    """Test retrieving tickets for a non-existent asset"""
    client, headers = user_client
    response = client.get("/tickets/99", headers=headers)
    assert response.status_code == 404
    assert "Asset with id 99 not found." in response.json["error"]


def test_get_asset_tickets_no_tickets(user_client, app):
    """Test retrieving tickets when the asset exists but has no tickets"""
    client, headers = user_client
    with app.app_context():
        asset = Asset.query.first()
        assert asset, "No asset found in database"
        db.session.query(Ticket).delete()
        db.session.commit()
        db.session.refresh(asset)
    response = client.get(f"/tickets/{asset.id}", headers=headers)
    assert response.status_code == 200
    assert response.json[asset.name] == []



def test_get_asset_tickets_unauthorized(client):
    """Test retrieving asset tickets without JWT token"""
    response = client.get("/tickets/1")
    assert response.status_code == 401


def test_get_asset_tickets_invalid_id(user_client):
    """Test retrieving asset tickets with an invalid asset ID format"""
    client, headers = user_client
    response = client.get("/tickets/invalid", headers=headers)
    assert response.status_code == 404


def test_get_asset_tickets_invalid_method(user_client):
    """Test accessing asset tickets with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/tickets/1", headers=headers)
    assert response.status_code == 405


@pytest.mark.xfail(reason="check on mock")
def test_get_asset_tickets_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during asset ticket retrieval
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB error"))
    response = client.get("/tickets/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
