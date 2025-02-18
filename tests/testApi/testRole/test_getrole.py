from app.models.v1 import Role
from app.extensions import db


def test_valid_role(user_client):
    """Test retrieving an existing role."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    response = client.get(f"/role/{role.id}", headers=headers)
    assert response.status_code == 200


def test_non_existent_role(user_client):
    """Test retrieving a non-existent role."""
    client, headers = user_client
    response = client.get("/role/999", headers=headers)
    assert response.status_code == 404
    assert "role with id 999 not found." in response.get_json()["error"]


def test_invalid_role_id(user_client):
    """Test invalid role ID format."""
    client, headers = user_client
    response = client.get("/role/abc", headers=headers)
    assert response.status_code == 404


def test_missing_token(user_client):
    """Test missing authentication token."""
    client, _ = user_client
    role = Role.query.filter_by(name="admin").first()
    response = client.get(f"/role/{role.id}")
    assert response.status_code == 401


def test_database_error_handling(user_client, mocker):
    """Test database failure during getting role"""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    assert role is not None
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB Error"))
    response = client.get(f'/role/{role.id}', headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
