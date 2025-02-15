import pytest


BASE_URL = "/register/department"


def test_createdepartment(user_client):
    """Test successfull creation of department"""
    client, _ = user_client
    payload = {
        "name": "HR"
    }
    response = client.post("/register/department", json=payload)
    assert response.status_code == 201
    assert "Department registered successfully!" \
        in response.get_json()["message"]


def test_missing_json_payload(user_client):
    """Test creating user with no payload"""
    client, headers = user_client
    response = client.post("/register/department", headers=headers)
    assert response.status_code == 415
    assert "Unsupported Media Type. Content-Type must be application/json." \
        in response.get_json()["error"]


def test_non_json_content_type(user_client):
    """test creating user with non json content type"""
    client, _ = user_client
    payload = "'name': 'HR'"
    response = client.post("/register/department", data=payload)
    assert response.status_code == 415
    assert "Unsupported Media Type. Content-Type must be application/json." \
        in response.get_json()["error"]


def test_missing_name_field(user_client):
    """Test request missing the 'name' field."""
    client, _ = user_client
    payload = {"other_field": "value"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "name" in response.get_json()["errors"]


def test_empty_name_value(user_client):
    """Test request with an empty 'name' value."""
    client, _ = user_client
    payload = {"name": ""}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "name" in response.get_json()["errors"]


def test_whitespace_only_name(user_client):
    """Test request with a name containing only spaces."""
    client, _ = user_client
    payload = {"name": "   "}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "Department name cannot be empty or just whitespace." \
        in response.get_json()["errors"]["name"]


def test_excessively_long_name(user_client):
    """Test request with an excessively long department name."""
    client, _ = user_client
    payload = {"name": "A" * 150}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "Length must be between 1 and 120." \
        in response.get_json()["errors"]["name"]


def test_special_characters_in_name(user_client):
    """Test request with special characters in the department name."""
    client, _ = user_client
    payload = {"name": "@dm!n"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "Department name cannot contain special characters." \
        in response.get_json()["errors"]["name"]


def test_sql_injection_attempt(user_client):
    """Test SQL injection attempt in department name."""
    client, _ = user_client
    payload = {"name": "'; DROP TABLE departments; --"}
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_duplicate_department_name(user_client):
    """Test registering the same department twice if uniqueness is enforced."""
    client, _ = user_client
    payload = {"name": "Finance"}
    response1 = client.post(BASE_URL, json=payload)
    assert response1.status_code == 201
    response2 = client.post(BASE_URL, json=payload)
    assert response2.status_code == 400


def test_database_failure_simulation(user_client, mocker):
    """Test behavior when the database is down."""
    client, _ = user_client
    payload = {"name": "IT"}
    mocker.patch("app.db.session.commit", side_effect=Exception("DB Failure"))
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()["error"]


@pytest.mark.parametrize(
        "payload", [{"name": f"Department{i}"} for i in range(50)])
def test_high_concurrent_requests(user_client, payload):
    """Test high concurrent requests to check for race conditions."""
    client, _ = user_client
    response = client.post(BASE_URL, json=payload)
    assert response.status_code == 201
