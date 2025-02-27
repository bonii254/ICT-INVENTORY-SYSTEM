from app.models.v1 import AssetTransfer


def test_delete_asset_transfer_success(user_client, app):
    """Test successfully deleting an existing asset transfer"""
    client, headers = user_client
    with app.app_context():
        asset_transfer = AssetTransfer.query.first()
        assert asset_transfer, "No asset transfer found in database"

    response = client.delete(
        f"/assettransfer/{asset_transfer.id}", headers=headers)
    assert response.status_code == 200
    assert "Asset transfer deleted successfully" in response.json["message"]

    response_check = client.get(
        f"/assettransfer/{asset_transfer.id}", headers=headers)
    assert response_check.status_code == 404


def test_delete_asset_transfer_not_found(user_client):
    """Test deleting a non-existent asset transfer"""
    client, headers = user_client
    response = client.delete("/assettransfer/99999", headers=headers)
    assert response.status_code == 404
    assert response.json["error"] == "Asset transfer not found"


def test_delete_asset_transfer_unauthorized(client):
    """Test deleting an asset transfer without JWT token"""
    response = client.delete("/assettransfer/1")
    assert response.status_code == 401


def test_delete_asset_transfer_invalid_method(user_client):
    """
    Test accessing asset transfer delete with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/assettransfer/1", headers=headers)
    assert response.status_code == 405


def test_delete_asset_transfer_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during delete"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    response = client.delete("/assettransfer/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
