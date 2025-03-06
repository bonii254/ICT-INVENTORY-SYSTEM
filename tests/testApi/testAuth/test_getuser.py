from app.models.v1 import User, Department, Role
from app.extensions import db


def test_user_not_found(user_client):
    """Test accessing non existing user"""
    client, headers = user_client
    response = client.get("/user/99", headers=headers)
    assert response.status_code == 404
    assert "User with id 99 not found" in response.json["Error"]


def test_missing_token(user_client):
    """Test missing access token"""
    client, headers = user_client
    response = client.get("/user/1")
    assert response.status_code == 401


def test_empty_user_id(user_client):
    """Test request with an empty user ID."""
    client, headers = user_client
    response = client.get("/user/", headers=headers)
    assert response.status_code == 404


def test_user_with_missing_field(user_client):
    """Test fetching a user whose fields are missing."""
    client, headers = user_client
    department = db.session.get(Department, 1)
    role = db.session.get(Role, 1)
    db.session.delete(department)
    db.session.delete(role)
    db.session.commit()

    response = client.get("/user/1", headers=headers)
    assert response.status_code == 200
    assert response.json["user"]["department"] == "Unknown Department"
    assert response.json["user"]["role"] == "Unknown Role"
