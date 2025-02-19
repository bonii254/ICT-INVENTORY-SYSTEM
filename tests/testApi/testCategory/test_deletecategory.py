from app.models.v1 import Category
from app.extensions import db


def test_delete_category_success(user_client):
    """Test successful category deletion"""
    client, headers = user_client
    category = Category.query.first()
    response = client.delete(f"/category/{category.id}", headers=headers)
    assert response.status_code == 200
    assert db.session.get(Category, category.id) is None
    assert "category deleted successfully" in response.get_json()["Message"]


def test_delete_category_not_found(user_client):
    """Test deleting a non-existent category"""
    client, headers = user_client
    response = client.delete("/category/9999", headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "Error" in data
    assert "category with id 9999 does not exist" in data["Error"]


def test_delete_category_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    response = client.delete("/category/1")
    assert response.status_code == 401


def test_delete_category_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit",
        side_effect=Exception("DB error"))
    response = client.delete("/category/1", headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occurred: DB error" in data["error"]


def test_delete_category_invalid_id(user_client):
    """Test invalid category ID (non-integer)"""
    client, headers = user_client
    response = client.delete("/category/non-integer", headers=headers)
    assert response.status_code == 405


def test_delete_category_rollback_on_failure(user_client, mocker):
    """Ensure DB rollback occurs after failure"""
    client, headers = user_client
    mock_delete = mocker.patch.object(
        db.session, "delete", side_effect=Exception("Deletion failed"))
    mock_rollback = mocker.patch.object(db.session, "rollback")
    response = client.delete("/category/1", headers=headers)
    assert response.status_code == 500
    mock_delete.assert_called_once()
    mock_rollback.assert_called_once()
