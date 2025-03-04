from app.models.v1 import Consumables
from app.extensions import db


def test_delete_consumable_success(user_client, app):
    """Test successfully deleting an existing consumable"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        consumable_id = consumable.id

    response = client.delete(f"/consumable/{consumable_id}", headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Consumable deleted successfully."

    with app.app_context():
        deleted_consumable = db.session.get(Consumables, consumable_id)
        assert deleted_consumable is None


def test_delete_consumable_not_found(user_client):
    """Test deleting a consumable that does not exist"""
    client, headers = user_client
    response = client.delete("/consumable/99", headers=headers)
    print(response.json)
    assert response.status_code == 404
    assert "Consumable with id 99 not found." in response.json["error"]


def test_delete_consumable_unauthorized(client):
    """Test deleting a consumable without authentication"""
    response = client.delete("/consumable/1")
    assert response.status_code == 401


def test_delete_consumable_invalid_id(user_client):
    """Test deleting a consumable with an invalid ID (non-integer)"""
    client, headers = user_client
    response = client.delete("/consumable/invalid_id", headers=headers)
    assert response.status_code == 404


def test_delete_consumable_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server errors during consumable deletion
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit",
        side_effect=Exception("DB error"))
    response = client.delete("/consumable/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occured" in response.json["error"]


def test_delete_consumable_already_deleted(user_client, app):
    """Test deleting a consumable that was already deleted"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables.query.first()
        consumable_id = consumable.id
        db.session.delete(consumable)
        db.session.commit()

    response = client.delete(f"/consumable/{consumable_id}", headers=headers)
    assert response.status_code == 404


def test_delete_consumable_invalid_method(user_client):
    """
    Test accessing the delete endpoint with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/consumable/1", headers=headers)
    assert response.status_code == 405
