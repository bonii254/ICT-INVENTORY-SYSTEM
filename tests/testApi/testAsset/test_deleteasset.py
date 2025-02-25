from app.extensions import db


def test_delete_asset_by_asset_tag(user_client):
    """Test deleting a single asset by asset tag."""
    client, headers = user_client
    response = client.delete(
        "/delete/assets?asset_tag=ASSET-001", headers=headers)
    assert response.status_code == 200
    assert "Successfully deleted 1 asset(s)." in response.get_json()["message"]


def test_delete_assets_by_category(user_client):
    """Test deleting multiple assets by category."""
    client, headers = user_client
    response = client.delete(
        "/delete/assets?category=Computers:Desktop", headers=headers)
    assert response.status_code == 200
    assert "Successfully deleted" in response.get_json()["message"]


def test_delete_assets_by_multiple_filters(user_client):
    """Test deleting assets by multiple filters."""
    client, headers = user_client
    response = client.delete(
        "/delete/assets?location=Plant&department=ICT", headers=headers)
    assert response.status_code == 200
    assert "Successfully deleted" in response.get_json()["message"]


def test_delete_assets_no_matching(user_client):
    """Test deleting assets that do not exist."""
    client, headers = user_client
    response = client.delete(
        "/delete/assets?name=NonExistentAsset", headers=headers)
    assert response.status_code == 404
    assert "No matching assets found for deletion" \
        in response.get_json()["error"]


def test_delete_assets_missing_jwt(client):
    """Test accessing delete endpoint without JWT token."""
    response = client.delete("/delete/assets")
    assert response.status_code == 401


def test_delete_assets_invalid_jwt(client):
    """Test accessing delete endpoint with an invalid JWT token."""
    response = client.delete(
        "/delete/assets",
        headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


def test_delete_assets_unexpected_error(mocker, user_client):
    """Test unexpected server error during asset deletion."""
    client, headers = user_client
    mocker.patch.object(
        db.session, "delete", side_effect=Exception("Deletion failed"))
    response = client.delete(
        "/delete/assets?asset_tag=ASSET-001", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()["error"]
