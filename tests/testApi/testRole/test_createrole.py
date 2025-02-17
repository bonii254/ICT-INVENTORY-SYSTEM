from app.extensions import db
from app.models.v1 import Role


def test_create_role_success(client):
    """
    Test Case: Successfully create a new role.
    """
    payload = {
        "name": "Superuser",
        "permissions": "read,write,update,delete"
    }
    response = client.post("/register/role", json=payload)
    assert response.status_code == 201
    assert "Role registered successfully!" in response.get_json()["message"]


def test_create_role_invalid_json(client):
    """
    Test Case: Invalid JSON structure (missing closing brace).
    """
    payload = {
        "name": "Superuser"
        "permissions" "read,write,update,delete"
    }
    response = client.post("/register/role", json=payload)
    assert response.status_code == 400


def test_create_role_unsupported_media_type(client):
    """
    Test Case: Content-Type is not JSON (415 Unsupported Media Type).
    """
    response = client.post(
        "/register/role",
        data="<role><name>Admin</name></role>",
        content_type="application/xml"
    )

    assert response.status_code == 415
    assert "Unsupported Media Type" in response.json["error"]


def test_create_role_missing_fields(mocker, client):
    """
    Test Case: Request body missing required fields.
    """
    payload = {
        "name": "Superuser",
    }
    response = client.post("/register/role", json=payload)
    assert response.status_code == 400
    assert "Missing data for required field." \
        in response.json["errors"]["permissions"]


def test_create_role_db_failure(mocker, client):
    """
    Test Case: Simulate database commit failure (500 Internal Server Error).
    """
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB Error"))

    payload = {
        "name": "Superuser",
        "permissions": "read,write,update,delete"
    }
    response = client.post("/register/role", json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred: DB Error" \
        in response.json["error"]
