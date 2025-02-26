from app.models.v1 import AssetTransfer
from app.extensions import db


def test_get_asset_transfer_success(user_client, app):
    """Test retrieving a specific asset transfer successfully"""
    client, headers = user_client
    with app.app_context():
        asset_transfer = AssetTransfer.query.first()
        assert asset_transfer, "No asset transfer found in database"
    response = client.get(
        f"/assettransfer/{asset_transfer.id}", headers=headers)
    assert response.status_code == 200
    assert "id" in response.json
    assert response.json["id"] == asset_transfer.id


def test_get_asset_transfer_not_found(user_client):
    """Test retrieving an asset transfer that does not exist"""
    client, headers = user_client
    response = client.get("/assettransfer/99999", headers=headers)
    assert response.status_code == 404
    assert response.json["error"] == "Asset transfer not found"


def test_get_asset_transfer_invalid_id(user_client):
    """Test retrieving an asset transfer with an invalid ID format"""
    client, headers = user_client
    response = client.get("/assettransfer/invalid", headers=headers)
    assert response.status_code == 404


def test_get_asset_transfer_unauthorized(client):
    """Test retrieving an asset transfer without JWT token"""
    response = client.get("/assettransfer/1")
    assert response.status_code == 401


def test_get_asset_transfer_invalid_method(user_client):
    """Test accessing asset transfer with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/assettransfer/1", headers=headers)
    assert response.status_code == 405


def test_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB error"))
    response = client.get("/assettransfer/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred: DB error" in response.json["error"]
