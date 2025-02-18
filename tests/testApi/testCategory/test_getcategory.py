from app.models.v1 import Category

def test_get_category_success(user_client):
    "Test retrieving an existing category."
    client, headers = user_client
    category = Category.query.first()
    response = client.get(f'/category/{category.id}', headers=headers)
    assert response.status_code == 200
    assert response.json['category']['id'] == category.id
    assert response.json['category']['name'] == category.name
    assert response.json['category']['description'] == category.description

def test_get_category_not_found(user_client):
    "Test retrieving a non-existent category."
    client, headers = user_client
    response = client.get('/category/9999', headers=headers)
    assert response.status_code == 404
    assert response.json['Error'] == "category with id 9999 does not exist"

def test_get_category_invalid_id(user_client):
    "Test retrieving a category with an invalid ID format."
    client, headers = user_client
    response = client.get('/category/invalid_id', headers=headers)
    assert response.status_code == 404

def test_get_category_missing_authentication(client):
    "Test retrieving a category without authentication."
    category = Category.query.first()
    response = client.get(f'/category/{category.id}')
    assert response.status_code == 401
    assert "error" in response.json
    assert "Authentication required" in response.json["error"]
