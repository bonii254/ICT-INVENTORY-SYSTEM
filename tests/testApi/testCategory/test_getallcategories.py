from app.models.v1 import Category
from app.extensions import db


def test_get_all_categories_success(user_client):
    """Test successful retrieval of categories"""
    client, headers = user_client

    response = client.get('/categories', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "categories" in data
    assert isinstance(data["categories"], list)
    if data["categories"]:
        assert "id" in data["categories"][0]
        assert "name" in data["categories"][0]
        assert "description" in data["categories"][0]


def test_get_all_categories_empty(user_client, app):
    """Test when no categories exist"""
    client, headers = user_client
    with app.app_context():
        Category.query.delete()
        db.session.commit()
    response = client.get('/categories', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "categories" in data
    assert data["categories"] == []


def test_get_all_categories_unauthorized(client):
    """Test request without JWT token"""
    response = client.get('/categories')
    assert response.status_code == 401


def test_get_all_categories_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    mocker.patch.object(
        Category, "query",
        new_callable=mocker.PropertyMock,
        side_effect=Exception("Unexpected error"))
    response = client.get('/categories', headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "Unexpected error" in data["error"]
