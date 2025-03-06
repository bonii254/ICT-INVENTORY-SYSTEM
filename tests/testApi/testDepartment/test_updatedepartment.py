from app.models.v1 import Department
from app.extensions import db


def test_successfull_update(user_client, app):
    """Test successful department update"""
    client, headers = user_client
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
        assert dept, "Department 'ICT' does not exist in the test database"
    payload = {"name": "Procurement"}
    response = client.put(
        f"/department/{dept.id}", headers=headers, json=payload)
    assert response.status_code == 200


def test_missing_json_payload(user_client, app):
    """Test update without a JSON body."""
    client, headers = user_client
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
        assert dept, "Department 'ICT' does not exist in the test database"
    response = client.put(
        f"/department/{dept.id}", headers=headers)
    assert response.status_code == 415


def test_department_not_found(user_client):
    """Test updating a non-existent department."""
    client, headers = user_client
    payload = {"name": "Procurement"}
    response = client.put(f"/department/99999", json=payload, headers=headers)
    assert response.status_code == 404


def test_missing_name_field(user_client, app):
    """Test update request missing 'name' field."""
    client, headers = user_client
    payload = {}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"/department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400


def test_empty_name_value(user_client, app):
    """Test updating with an empty name."""
    client, headers = user_client
    payload = {"name": ""}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Length must be between 1 and 120." \
        in response.get_json()["errors"]["name"]


def test_whitespace_only_name(user_client, app):
    """Test updating with a name containing only spaces."""
    client, headers = user_client
    payload = {"name": "   "}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Department name cannot be empty or just whitespace." \
        in response.get_json()["errors"]["name"]


def test_excessively_long_name(user_client, app):
    """Test updating with a very long department name."""
    client, headers = user_client
    payload = {"name": "A" * 150}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Length must be between 1 and 120." \
        in response.get_json()["errors"]["name"]


def test_special_characters_in_name(user_client, app):
    """Test updating with special characters in name."""
    client, headers = user_client
    payload = {"name": "@dm!n"}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Department name cannot contain special characters." \
        in response.get_json()["errors"]["name"]


def test_duplicate_department_name(user_client, app):
    """Test updating department name to an existing one."""
    client, headers = user_client
    payload = {"name": "ICT"}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    response = client.put(
        f"department/{dept.id}", json=payload, headers=headers)
    assert response.status_code == 400
    assert "Department name 'ICT' already exists." \
        in response.get_json()["errors"]["name"]


def test_invalid_department_id(user_client, app):
    """Test updating with a non-integer department ID."""
    client, headers = user_client
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    payload = {"name": "Procurement"}
    response = client.put(
        "/department/99", headers=headers, json=payload)
    assert response.status_code == 404
    assert "Department with ID 99 not found." \
        in response.get_json()["error"]


def test_negative_department_id(user_client, app):
    """Test updating with a negative department ID."""
    client, headers = user_client
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    payload = {"name": "Procurement"}
    response = client.put(
        "/department/-1", headers=headers, json=payload)
    assert response.status_code == 405


def test_unauthorized_access(user_client, app):
    """Test update without authentication token."""
    client, _ = user_client
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    payload = {"name": "Procurement"}
    response = client.put(
        f"/department/{dept.id}", json=payload)
    assert response.status_code == 401
    assert "Authentication required" \
        in response.get_json()["error"]


def test_invalid_jwt_token(user_client, app):
    """Test update with an invalid JWT token."""
    client, _ = user_client
    headers = {"Authorization": "Bearer refresh_token"}
    with app.app_context():
        dept = Department.query.filter_by(name="ICT").first()
    payload = {"name": "Procurement"}
    response = client.put(
        f"/department/{dept.id}", headers=headers, json=payload)
    assert response.status_code == 401
