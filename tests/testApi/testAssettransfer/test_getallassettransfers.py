from app.models.v1 import AssetTransfer
from app.extensions import db


def test_get_all_asset_transfers(user_client):
    """Test retrieving all asset transfers successfully"""
    client, headers = user_client
    response = client.get("/assettransfers", headers=headers)
    assert response.status_code == 200
    assert "asset_transfers" in response.json
    assert isinstance(response.json["asset_transfers"], list)


def test_get_all_asset_transfers_no_data(user_client, app):
    """Test retrieving asset transfers when no transfers exist"""
    client, headers = user_client
    with app.app_context():
        db.session.query(AssetTransfer).delete()
        db.session.commit()
    response = client.get("/assettransfers", headers=headers)
    assert response.status_code == 200
    assert response.json["asset_transfers"] == []


def test_get_all_asset_transfers_unauthorized(client):
    """Test retrieving asset transfers without JWT token"""
    response = client.get("/assettransfers")
    assert response.status_code == 401


def test_get_all_asset_transfers_invalid_method(user_client):
    """Test accessing asset transfers with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/assettransfers", headers=headers)
    assert response.status_code == 405


def test_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error"""
    client, headers = user_client
    mocker.patch.object(
       AssetTransfer, "query",
       new_callable=mocker.PropertyMock,
       side_effect=Exception("DB error"))
    response = client.get("/assettransfers", headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "An unexpected error occurred: DB error" in data["error"]
