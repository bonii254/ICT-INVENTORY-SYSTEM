from app.models.v1 import AssetTransfer
from app.extensions import db


def test_search_asset_transfers_success(user_client, app):
    """Test searching asset transfers with valid filters"""
    client, headers = user_client
    with app.app_context():
        asset_transfer = AssetTransfer.query.first()
        assert asset_transfer, "No asset transfer found in database"
    response = client.get(
        f"/assettransfer/search?asset_id={asset_transfer.asset_id}",
        headers=headers)
    assert response.status_code == 200
    assert "asset_transfers" in response.json
    assert isinstance(response.json["asset_transfers"], list)
    assert len(response.json["asset_transfers"]) > 0


def test_search_no_results(user_client):
    """Test searching asset transfers with a non-matching filter"""
    client, headers = user_client
    response = client.get(
        "/assettransfer/search?asset_id=99999",
        headers=headers)
    assert response.status_code == 200
    assert response.json["asset_transfers"] == []


def test_search_multiple_filters(user_client, app):
    """Test searching asset transfers using multiple query parameters"""
    client, headers = user_client
    with app.app_context():
        asset_transfer = AssetTransfer.query.first()
        assert asset_transfer, "No asset transfer found in database"
    asset_id = asset_transfer.asset_id
    transferred_to = asset_transfer.transferred_to
    response = client.get(
        f"/assettransfer/search?\
            asset_id={asset_id}&transferred_to={transferred_to}",
        headers=headers
    )
    assert response.status_code == 200
    assert "asset_transfers" in response.json
    assert isinstance(response.json["asset_transfers"], list)


def test_search_asset_transfers_unauthorized(client):
    """Test searching asset transfers without JWT token"""
    response = client.get("/assettransfer/search")
    assert response.status_code == 401


def test_search_asset_transfers_invalid_method(user_client):
    """Test accessing search with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/assettransfer/search", headers=headers)
    assert response.status_code == 405
