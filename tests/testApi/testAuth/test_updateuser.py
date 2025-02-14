from app.models.v1 import Department, User
from app.extensions import db


def test_valid_user_update(user_client):
    client, headers = user_client
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    payload = {
        'department_id': dept.id
    }
    response = client.put("/auth/update/1", headers=headers, json=payload)
    assert response.status_code == 200
    assert "User Updated" in response.get_json()["Success"]


def test_missing_token(user_client):
    """Test updating user without a JWT token."""
    client, _ = user_client
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    payload = {
        'department_id': dept.id
    }
    response = client.put("/auth/update/1", json=payload)
    assert response.status_code == 401


def test_invalid_token(user_client):
    """Test updating user with an invalid JWT token."""
    client, _ = user_client
    headers = {"Authorization": "Bearer invalid.token.string"}
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    payload = {
        'department_id': dept.id
    }
    response = client.put("/auth/update/1", headers=headers, json=payload)
    assert response.status_code == 422


def test_user_not_found(user_client):
    """Test updating a non-existing user."""
    client, headers = user_client
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    payload = {
        'department_id': dept.id
    }
    response = client.put("/auth/update/55", headers=headers, json=payload)
    assert response.status_code == 404


def test_missing_json_body(user_client):
    """Test updating user without a JSON body."""
    client, headers = user_client
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    response = client.put("/auth/update/1", headers=headers)
    assert response.status_code == 415
    assert "Unsupported Media Type. Content-Type must be application/json." \
        in response.get_json()["error"]


def test_invalid_role_or_department(user_client):
    """Test updating user with a non-existing role or department."""
    client, headers = user_client
    payload = {
        'department_id': 55,
        'role_id': 65
    }
    response = client.put("/auth/update/1", headers=headers, json=payload)
    assert response.status_code == 400


def test_database_error_handling(user_client, mocker):
    """Test database failure during user update."""
    client, headers = user_client
    dept = Department(name="HR")
    db.session.add(dept)
    db.session.commit()
    payload = {
        'department_id': dept.id
    }
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB Error"))

    response = client.put("/auth/update/1", headers=headers, json=payload)
    assert response.status_code == 500
