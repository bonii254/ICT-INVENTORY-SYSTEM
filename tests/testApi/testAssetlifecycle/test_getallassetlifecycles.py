from app.models.v1 import AssetLifecycle
from app.extensions import db


def test_get_all_asset_lifecycles_success(user_client):
    """Test retrieving all asset lifecycle records successfully"""
    client, headers = user_client
    response = client.get("/asset-lifecycles", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json, list)
    assert len(response.json) > 0


def test_get_all_asset_lifecycles_no_data(user_client, app):
    """Test retrieving asset lifecycle records when none exist"""
    client, headers = user_client
    with app.app_context():
        db.session.query(AssetLifecycle).delete()
        db.session.commit()

    response = client.get("/asset-lifecycles", headers=headers)
    assert response.status_code == 200
    assert response.json == []


def test_get_all_asset_lifecycles_unauthorized(client):
    """Test retrieving asset lifecycle records without JWT token"""
    response = client.get("/asset-lifecycles")
    assert response.status_code == 401


def test_get_all_asset_lifecycles_invalid_method(user_client):
    """
    Test accessing asset lifecycle retrieval with an
    unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/asset-lifecycles", headers=headers)
    assert response.status_code == 405


def test_get_all_asset_lifecycles_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during asset lifecycle retrieval
    """
    client, headers = user_client
    mocker.patch.object(
       AssetLifecycle, "query",
       new_callable=mocker.PropertyMock,
       side_effect=Exception("DB error"))

    response = client.get("/asset-lifecycles", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
