from app.models.v1 import AssetLifecycle
from app.extensions import db


def test_update_asset_lifecycle_success(user_client, app):
    """Test successfully updating an asset lifecycle record"""
    client, headers = user_client
    with app.app_context():
        lifecycle = AssetLifecycle.query.first()
        lc_id = lifecycle.id
    payload = {"event": "Maintenance", "notes": "Routine maintenance check"}
    response = client.put(f"/asset-lifecycles/{lc_id}",
                          headers=headers, json=payload)
    assert response.status_code == 200
    assert response.json["event"] == "Maintenance"
    assert response.json["notes"] == "Routine maintenance check"


def test_update_asset_lifecycle_not_found(user_client):
    """Test updating a non-existent asset lifecycle record"""
    client, headers = user_client
    payload = {"event": "Repair", "notes": "Updated notes"}
    response = client.put(
        "/asset-lifecycles/99", headers=headers, json=payload)
    assert response.status_code == 404
    assert "Event with id 99 not found." in response.get_json()["error"]


def test_update_asset_lifecycle_invalid_content_type(user_client):
    """Test updating an asset lifecycle record with invalid Content-Type"""
    client, headers = user_client
    payload = {"event": "Transfer", "notes": "Moved to another location"}
    response = client.put("/asset-lifecycles/1", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_update_asset_lifecycle_invalid_data_types(user_client):
    """Test updating an asset lifecycle record with invalid data types"""
    client, headers = user_client
    payload = {"event": 12345, "notes": ["Invalid note format"]}
    response = client.put("/asset-lifecycles/1", headers=headers, json=payload)
    assert response.status_code == 400


def test_update_asset_lifecycle_unauthorized(client):
    """Test updating an asset lifecycle record without JWT token"""
    payload = {"event": "Inspection", "notes": "Unauthorized update attempt"}
    response = client.put("/asset-lifecycles/1", json=payload)
    assert response.status_code == 401


def test_update_asset_lifecycle_invalid_method(user_client):
    """
    Test accessing the update endpoint with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/asset-lifecycles/1", headers=headers)
    assert response.status_code == 405


def test_update_asset_lifecycle_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during asset lifecycle update
    """
    client, headers = user_client
    mocker.patch("app.extensions.db.session.commit",
                 side_effect=Exception("DB error"))
    payload = {"event": "Maintenance", "notes": "Routine maintenance"}
    response = client.put("/asset-lifecycles/1", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
