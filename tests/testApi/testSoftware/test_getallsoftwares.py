from app.models.v1 import Software
from app.extensions import db


def test_get_all_software_success(user_client, app):
    """Test retrieving all software records successfully"""
    client, headers = user_client
    response = client.get("/softwares", headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)


def test_get_all_software_no_data(user_client, app):
    """Test retrieving all software records when no software exists"""
    client, headers = user_client
    with app.app_context():
        db.session.query(Software).delete()
        db.session.commit()
    response = client.get("/softwares", headers=headers)
    assert response.status_code == 200
    assert response.json["Softwares"] == []


def test_get_all_software_unauthorized(client):
    """Test retrieving all software records without JWT token"""
    response = client.get("/softwares")
    assert response.status_code == 401


def test_get_all_software_invalid_method(user_client):
    """
    Test accessing all software records with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/softwares", headers=headers)
    assert response.status_code == 405
