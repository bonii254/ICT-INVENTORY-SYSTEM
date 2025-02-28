from app.models.v1 import Software
from app.extensions import db


def test_delete_software_success(user_client, app):
    """Test successfully deleting a software record"""
    client, headers = user_client
    with app.app_context():
        software = Software(
            name="Test Software", version="1.0", license_key="TEST-123")
        db.session.add(software)
        db.session.commit()
        software_id = software.id

    response = client.delete(f"/software/{software_id}", headers=headers)
    assert response.status_code == 201
    assert "software deleted successfully" in response.json["Message"]

    with app.app_context():
        deleted_software = db.session.get(Software, software_id)
        assert deleted_software is None


def test_delete_software_not_found(user_client):
    """Test deleting a non-existent software record"""
    client, headers = user_client
    response = client.delete("/software/99999", headers=headers)
    assert response.status_code == 404
    assert "Software with id 99999 not found" in response.json["error"]


def test_delete_software_unauthorized(client):
    """Test deleting a software record without JWT token"""
    response = client.delete("/software/1")
    assert response.status_code == 401


def test_delete_software_invalid_method(user_client):
    """
    Test accessing delete software endpoint with an
    unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/software/1", headers=headers)
    assert response.status_code == 405


def test_delete_software_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during software deletion"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    response = client.delete("/software/1", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
