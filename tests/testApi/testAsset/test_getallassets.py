from app.models.v1 import Asset
from app.extensions import db


def test_get_all_assets_success(user_client):
    """Test retrieving all assets successfully."""
    client, headers = user_client
    db.session.query(Asset).delete()
    response = client.get("/assets", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "assets" in data
    assert isinstance(data["assets"], list)
    assert len(data["assets"]) >= 0


def test_get_assets_empty(user_client):
    """Test retrieving assets when none exist in the database."""
    client, headers = user_client
    db.session.query(Asset).delete()
    db.session.commit()
    response = client.get("/assets", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "assets" in data
    assert isinstance(data["assets"], list)
    assert len(data["assets"]) == 0


def test_get_assets_missing_jwt(client):
    """Test accessing endpoint without JWT token."""
    response = client.get("/assets")
    assert response.status_code == 401
    assert "error" in response.get_json()
    assert response.get_json()["error"] == "Authentication required"


def test_get_assets_invalid_jwt(client):
    """Test accessing endpoint with an invalid JWT token."""
    response = client.get(
        "/assets", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
