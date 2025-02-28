from app.models.v1 import AssetLifecycle, Asset
from app.extensions import db
import pytest


def test_get_asset_lifecycles_by_asset_success(user_client, app):
    """Test retrieving all asset lifecycle records for a specific asset"""
    client, headers = user_client
    response = client.get(f"/assets/1/lifecycles", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_get_asset_lifecycles_by_asset_no_records(user_client, app):
    """
    Test retrieving asset lifecycle records when none exist for the asset
    """
    client, headers = user_client
    with app.app_context():
        db.session.query(AssetLifecycle).delete()
        db.session.commit()
        asset = Asset.query.first()
        asset_id = asset.id
    response = client.get(f"/assets/{asset_id}/lifecycles", headers=headers)
    assert response.status_code == 200
    assert response.json == []


def test_get_asset_lifecycles_by_asset_not_found(user_client):
    """Test retrieving asset lifecycle records for a non-existent asset"""
    client, headers = user_client
    response = client.get("/assets/99/lifecycles", headers=headers)
    print(response.json)
    assert response.status_code == 404
    assert "Asset with id 99 not found." in response.json["error"]


def test_get_asset_lifecycles_by_asset_unauthorized(client):
    """Test retrieving asset lifecycle records without JWT token"""
    response = client.get("/assets/1/lifecycles")
    assert response.status_code == 401


def test_get_asset_lifecycles_by_asset_invalid_method(user_client):
    """Test accessing the endpoint with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/assets/1/lifecycles", headers=headers)
    assert response.status_code == 405


def test_get_asset_lifecycles_by_asset_internal_server_error(
        user_client, mocker):
    """
    Test handling of unexpected server error during asset lifecycle retrieval
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get",
        side_effect=Exception("DB error")
    )
    response = client.get("/assets/1/lifecycles", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
