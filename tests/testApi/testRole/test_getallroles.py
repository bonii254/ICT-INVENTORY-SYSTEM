from app.extensions import db
from app.models.v1 import Role


def test_get_all_roles(user_client):
    """Test retrieving all roles successfully."""
    client, headers = user_client
    response = client.get("/roles", headers=headers)
    assert response.status_code == 200
    assert "roles" in response.get_json()


def test_get_all_roles_missing_token(user_client):
    """Test retrieving all roles without an authentication token."""
    client, _ = user_client
    response = client.get("/roles")
    assert response.status_code == 401


def test_get_all_roles_empty(user_client, app):
    """Test retrieving all roles when no roles exist."""
    client, headers = user_client
    with app.app_context():
        Role.query.delete()
        db.session.commit()
    response = client.get("/roles", headers=headers)
    assert response.status_code == 200
    assert len(response.get_json()["roles"]) == 0
