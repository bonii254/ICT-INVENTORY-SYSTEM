from app.models.v1 import Category
from app.extensions import db


def test_create_category_success(user_client):
    """Test creating a new category with valid data."""
    client, headers = user_client
    payload = {
        "name": "computing",
        "description": "All computing devices"
    }
    response = client.post('/register/category', json=payload, headers=headers)
    assert response.status_code == 201
    assert "Category registered successfully!" \
        in response.get_json()["message"]
    assert 'Category' in response.json
    assert response.json['Category']['name'] == "Computing"
    assert response.json['Category']['description'] == "All computing devices"


def test_create_category_invalid_json(user_client):
    """Test if invalid JSON is passed (non-JSON content)."""
    client, headers = user_client
    response = client.post(
        '/register/category', data="Invalid data", headers=headers)
    assert response.status_code == 415
    assert "Unsupported Media Type. Content-Type must be application/json." \
        in response.get_json()["error"]


def test_create_category_missing_fields(user_client):
    """Test if required fields are missing from the payload."""
    client, headers = user_client
    payload = {"name": "networking"}
    response = client.post('/register/category', json=payload, headers=headers)
    assert response.status_code == 400
    assert 'errors' in response.json
    assert "description" in response.json['errors']


def test_create_category_invalid_field_type(user_client):
    """Test if invalid data types are passed in the payload."""
    client, headers = user_client
    payload = {
        "name": 12345,
        "description": "Valid description"
    }
    response = client.post('/register/category', json=payload, headers=headers)
    assert response.status_code == 400
    assert 'errors' in response.json
    assert 'Not a valid string.' in response.json['errors']['name']


def test_create_category_missing_authentication(client):
    """Test if JWT token is missing in the request headers."""
    payload = {
        "name": "New Category",
        "description": "Description of new category"
    }
    response = client.post('/register/category', json=payload)
    assert response.status_code == 401
    assert "error" in response.json
    assert "Authentication required" in response.json["error"]


def test_create_category_invalid_authentication(client):
    """Test if an invalid JWT token is provided."""
    headers = {'Authorization': "Bearer invalid_token"}
    payload = {
        "name": "New Category",
        "description": "Description of new category"
    }
    response = client.post('/register/category', json=payload, headers=headers)
    assert response.status_code == 401
    assert "error" in response.json
    assert "Invalid token" in response.json["error"]


def test_create_category_database_error(user_client, mocker):
    """Test if there is a database error (e.g., commit failure)."""
    client, headers = user_client
    payload = {
        "name": "computing",
        "description": "All computing devices"
    }
    mocker.patch(
        'app.db.session.commit', side_effect=Exception(
            "Database commit error"))
    response = client.post('/register/category', json=payload, headers=headers)
    assert response.status_code == 500
    assert "error" in response.json
    assert "An unexpected error occurred" in response.json["error"]
