from app.models.v1 import AssetLifecycle
from app.extensions import db


def test_delete_asset_lifecycle_success(user_client, app):
    """Test successfully deleting an asset lifecycle record"""
    client, headers = user_client
    with app.app_context():
        event = AssetLifecycle.query.first()
        event_id = event.id

    response = client.delete(f"/asset-lifecycles/{event_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Deleted successfully"

    with app.app_context():
        deleted_lifecycle = db.session.get(AssetLifecycle, event_id)
        assert deleted_lifecycle is None


def test_delete_asset_lifecycle_not_found(user_client):
    """Test deleting a non-existent asset lifecycle record"""
    client, headers = user_client
    response = client.delete("/asset-lifecycles/99", headers=headers)
    assert response.status_code == 404
    assert "Event with id 99 not found." in response.get_json()["error"]


def test_delete_asset_lifecycle_unauthorized(client):
    """Test deleting an asset lifecycle record without JWT token"""
    response = client.delete("/asset-lifecycles/1")
    assert response.status_code == 401


def test_delete_asset_lifecycle_invalid_method(user_client):
    """
    Test accessing delete endpoint with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/asset-lifecycles/1", headers=headers)
    assert response.status_code == 405


def test_delete_asset_lifecycle_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during deletion"""
    client, headers = user_client
    mocker.patch("app.extensions.db.session.commit",
                 side_effect=Exception("DB error"))
    response = client.delete("/asset-lifecycles/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
