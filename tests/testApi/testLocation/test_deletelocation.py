from app.models.v1 import Location
from app.extensions import db


def test_delete_location_success(user_client):
    """Test successful location deletion"""
    client, headers = user_client
    location = Location.query.first()
    response = client.delete(f"/location/{location.id}", headers=headers)
    print(response.json)
    assert response.status_code == 200
    data = response.get_json()
    assert "Message" in data
    assert data["Message"] == "Location deleted successfully"
    assert db.session.get(Location, location.id) is None


def test_delete_location_not_found(user_client):
    """Test deleting a non-existent location"""
    client, headers = user_client
    response = client.delete("/location/9999", headers=headers)
    assert response.status_code == 404
    data = response.get_json()
    assert "Error" in data
    assert "Location with id 9999 does not exist" in data["Error"]


def test_delete_location_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    location = Location.query.first()
    response = client.delete(f"/location/{location.id}")
    assert response.status_code == 401


def test_delete_location_invalid_id(user_client):
    """Test invalid location ID (non-integer)"""
    client, headers = user_client
    response = client.delete("/location/invalid_id", headers=headers)
    assert response.status_code == 404


def test_delete_location_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    location = Location.query.first()
    mocker.patch.object(
        db.session, "commit", side_effect=Exception("DB error"))
    response = client.delete(f"/location/{location.id}", headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occurred: DB error" in data["error"]


def test_delete_location_rollback_on_failure(user_client, mocker):
    """Ensure DB rollback occurs after failure"""
    client, headers = user_client
    location = Location.query.first()
    mock_delete = mocker.patch.object(
        db.session, "delete", side_effect=Exception("Deletion failed"))
    mock_rollback = mocker.patch.object(db.session, "rollback")
    response = client.delete(f"/location/{location.id}", headers=headers)
    assert response.status_code == 500
    mock_delete.assert_called_once()
    mock_rollback.assert_called_once()
