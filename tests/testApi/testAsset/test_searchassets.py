import pytest


def test_search_assets_by_name(user_client):
    """Test searching assets by name."""
    client, headers = user_client
    response = client.get("/assets/search?name=Laptop", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "assets" in data
    assert len(data["assets"]) > 0
    assert any("Laptop" in asset["name"] for asset in data["assets"])


def test_search_assets_by_asset_tag(user_client):
    """Test searching assets by asset tag."""
    client, headers = user_client
    response = client.get(
        "/assets/search?asset_tag=ASSET-001", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["assets"]) == 1


def test_search_assets_pagination(user_client):
    """Test pagination in search results."""
    client, headers = user_client
    response = client.get("/assets/search?page=1&per_page=1", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "assets" in data
    assert len(data["assets"]) == 1


def test_search_assets_no_results(user_client):
    """Test searching for non-existent assets."""
    client, headers = user_client
    response = client.get("/assets/search?name=NonExistent", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "assets" in data
    assert len(data["assets"]) == 0


def test_search_assets_missing_jwt(client):
    """Test accessing search endpoint without JWT token."""
    response = client.get("/assets/search")
    assert response.status_code == 401


def test_search_assets_invalid_jwt(client):
    """Test accessing search endpoint with an invalid JWT token."""
    response = client.get(
        "/assets/search", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401


@pytest.mark.xfail(reason="Database failure handling needs improvement")
def test_search_assets_database_failure(mocker, user_client):
    """Test database failure during asset search."""
    client, headers = user_client
    mocker.patch(
        "app.models.v1.Asset.query.paginate",
        side_effect=Exception("DB Error"))
    response = client.get("/assets/search", headers=headers)
    assert "DB Error" in response.get_json()["error"]
    assert response.status_code == 500
    assert "error" in response.get_json()
