from app.models.v1 import AssetLifecycle
from app.extensions import db


def test_get_asset_lifecycle_success(user_client, app):
    """Test retrieving a specific asset lifecycle record successfully"""
    client, headers = user_client
    with app.app_context():
        event = AssetLifecycle(
            asset_id=1, event="Maintenance", notes="Routine check completed")
        db.session.add(event)
        db.session.commit()
        event_id = event.id

    response = client.get(f"/asset-lifecycles/{event_id}", headers=headers)
    assert response.status_code == 200
    assert "event" in response.json
    assert response.json["event"] == "Maintenance"


def test_get_asset_lifecycle_not_found(user_client):
    """Test retrieving a non-existent asset lifecycle record"""
    client, headers = user_client
    response = client.get("/asset-lifecycles/99999", headers=headers)
    assert response.status_code == 404


def test_get_asset_lifecycle_unauthorized(client):
    """Test retrieving an asset lifecycle record without JWT token"""
    response = client.get("/asset-lifecycles/1")
    assert response.status_code == 401


def test_get_asset_lifecycle_invalid_id(user_client):
    """Test retrieving an asset lifecycle record with an invalid ID format"""
    client, headers = user_client
    response = client.get("/asset-lifecycles/invalid", headers=headers)
    assert response.status_code == 404


def test_get_asset_lifecycle_invalid_method(user_client):
    """Test accessing asset lifecycle retrieval with an
    unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/asset-lifecycles/1", headers=headers)
    assert response.status_code == 405


def test_get_asset_lifecycle_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during asset lifecycle retrieval
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get",
        side_effect=Exception("DB error"))
    response = client.get("/asset-lifecycles/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
