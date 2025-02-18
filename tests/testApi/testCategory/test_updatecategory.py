from app.models.v1 import Category


def test_update_category_success(user_client):
    """Test updating a category with valid data."""
    client, headers = user_client
    category = Category.query.first()
    payload = {
        "name": "Updated Category",
        "description": "Updated description"
    }
    response = client.put(
        f'/category/{category.id}', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json['Message'] == "category updated successfully"
    assert response.json['category']['name'] == "Updated category"
    assert response.json['category']['description'] == "Updated description"


def test_update_category_invalid_json(user_client):
    """Test if invalid JSON is passed (non-JSON content)."""
    client, headers = user_client
    category = Category.query.first()
    response = client.put(
        f'/category/{category.id}', data="Invalid data", headers=headers)
    assert response.status_code == 415
    assert "Unsupported Media Type. Content-Type must be application/json." \
        in response.get_json()["error"]


def test_update_category_not_found(user_client):
    """Test if the category ID does not exist."""
    client, headers = user_client
    response = client.put(
        '/category/9999',
        json={"name": "Nonexistent Category"},
        headers=headers)
    assert response.status_code == 404
    assert response.json['error'] == "category with ID 9999 not found."


def test_update_category_missing_fields(user_client):
    """Test if required fields are missing from the payload."""
    client, headers = user_client
    category = Category.query.first()
    payload = {"name": "New Category"}
    response = client.put(
        f'/category/{category.id}', json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json['category']['name'] == "New category"
    assert response.json['category']['description'] == category.description


def test_update_category_invalid_field_type(user_client):
    """Test if invalid data types are passed in the payload."""
    client, headers = user_client
    category = Category.query.first()
    payload = {
        "name": 12345,
        "description": "Valid description"
    }
    response = client.put(
        f'/category/{category.id}', json=payload, headers=headers)
    assert response.status_code == 400
    assert 'errors' in response.json
    assert 'name' in response.json['errors']


def test_update_category_missing_authentication(client):
    """Test if JWT token is missing in the request headers."""
    category = Category.query.first()
    payload = {
        "name": "Updated Category",
        "description": "Updated description"
    }
    response = client.put(f'/category/{category.id}', json=payload)
    assert response.status_code == 401
    assert "error" in response.json
    assert "Authentication required" in response.json["error"]


def test_update_category_empty_payload(user_client):
    """Test if an empty payload is passed."""
    client, headers = user_client
    category = Category.query.first()
    response = client.put(f'/category/{category.id}', json={}, headers=headers)
    assert response.status_code == 200


def test_update_category_database_error(user_client, mocker):
    """Test if there is a database error (e.g., commit failure)."""
    client, headers = user_client
    category = Category.query.first()
    payload = {
        "name": "Updated Category",
        "description": "Updated description"
    }
    mocker.patch(
        'app.extensions.db.session.commit',
        side_effect=Exception("Database commit error"))
    response = client.put(
        f'/category/{category.id}', json=payload, headers=headers)
    assert response.status_code == 500
    assert "error" in response.json
    assert "An unexpected error occurred" in response.json["error"]
