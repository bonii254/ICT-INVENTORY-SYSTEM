from app.models.v1 import Role
from app.extensions import db


def test_delete_role_success(user_client):
    """Test successful deletion of a role by ID."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    response = client.delete(f"/role/{role.id}", headers=headers)
    assert response.status_code == 200
    assert response.get_json()["Message"] == "role deleted successfully"


def test_delete_role_not_found(user_client):
    """Test trying to delete a role that does not exist."""
    client, headers = user_client
    response = client.delete("/role/999", headers=headers)
    assert response.status_code == 404
    assert "Error" in response.get_json()


def test_delete_role_missing_token(client):
    """Test missing JWT token in the request."""
    response = client.delete("/role/1")
    assert response.status_code == 401


def test_delete_role_invalid_token(user_client):
    """Test invalid JWT token in the request."""
    client, _ = user_client
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.delete("/role/1", headers=headers)
    assert response.status_code == 401


def test_delete_role_database_error(user_client, mocker):
    """Test database error when deleting a role."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    mocker.patch.object(
        db.session, "commit", side_effect=Exception("DB Error"))
    response = client.delete(f"/role/{role.id}", headers=headers)
    assert response.status_code == 500
    assert "error" in response.get_json()


def test_delete_role_wrong_method(user_client):
    """
    Test calling delete with the wrong HTTP method
    (e.g., POST instead of DELETE).
    """
    client, headers = user_client
    response = client.post("/role/1", headers=headers)
    assert response.status_code == 405


def test_delete_role_invalid_id_format(user_client):
    """Test invalid role ID format (e.g., non-integer)."""
    client, headers = user_client
    response = client.delete("/role/abc", headers=headers)
    assert response.status_code == 404
