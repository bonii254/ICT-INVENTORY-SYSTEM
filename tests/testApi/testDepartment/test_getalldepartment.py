from app.models.v1 import Department
from app.extensions import db


def test_get_all_departments_with_data(user_client):
    """Valid case: Returns all departments."""
    client, headers = user_client
    response = client.get("/departments", headers=headers)
    assert response.status_code == 200
    assert len(response.json["departments"]) == 1


def test_get_all_departments_empty(user_client, app):
    """Valid case: Returns empty list when no departments exist."""
    client, headers = user_client
    with app.app_context():
        Department.query.delete()
        db.session.commit()

    response = client.get("/departments", headers=headers)
    assert response.status_code == 200
    assert response.json["departments"] == []


def test_get_all_departments_missing_jwt(user_client):
    """Unauthorized case: Missing JWT token should return 401."""
    client, _ = user_client
    response = client.get("/departments")
    assert response.status_code == 401
    assert "Missing token" in response.get_json()["error"]


def test_get_all_departments_invalid_jwt(user_client):
    """Unauthorized case: Invalid JWT token should return 401."""
    client, _ = user_client
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/departments", headers=headers)
    assert response.status_code == 401
    assert "Invalid token" in response.get_json()["error"]
