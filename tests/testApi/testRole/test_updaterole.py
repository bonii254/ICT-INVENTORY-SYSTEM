from app.models.v1 import Role
from app.extensions import db


def test_update_role_success(user_client):
    """Updates a role successfully."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    payload = {
        "name": "user",
        "permissions": "read,write,update"
    }
    response = client.put(f"/role/{role.id}", headers=headers, json=payload)
    assert response.status_code == 200


def test_update_role_not_found(user_client):
    """Returns 404 when role does not exist."""
    client, headers = user_client
    payload = {
        "name": "user",
        "permissions": "read,write,update"
    }
    response = client.put("/role/999", headers=headers, json=payload)
    assert response.status_code == 404


def test_update_role_invalid_json(user_client):
    """Returns 400 for invalid JSON format."""
    client, headers = user_client
    response = client.put("/role/1", data="invalid json", headers=headers)
    assert response.status_code == 415


def test_update_role_missing_json(user_client):
    """Returns 415 when Content-Type is not application/json."""
    client, headers = user_client
    response = client.put("/role/1", headers=headers)
    assert response.status_code == 415


def test_update_role_partial_update(user_client):
    """Allows partial updates to role name."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    payload = {
        "name": "user"
    }
    response = client.put(f"/role/{role.id}", headers=headers, json=payload)
    assert response.status_code == 200
    assert "user" in response.json["role"]["name"]


def test_update_role_duplicate_name(user_client):
    """Returns 400 when updating role to an existing name."""
    client, headers = user_client
    role = Role.query.filter_by(name="admin").first()
    payload = {
        "name": "admin",
        "permissions": "read,write,update"
    }
    response = client.put(f"/role/{role.id}", headers=headers, json=payload)
    assert response.status_code == 400
    assert "Role name 'admin' already exists." \
        in response.get_json()["errors"]["name"]


def test_update_role_db_failure(mocker, user_client):
    """
    Test Case: Simulate database commit failure (500 Internal Server Error).
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB Error"))

    payload = {
        "name": "Superuser",
        "permissions": "read,write,update,delete"
    }
    role = Role.query.filter_by(name="admin").first()
    response = client.put(
        f"/role/{role.id}", json=payload, headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred: DB Error" \
        in response.json["error"]
