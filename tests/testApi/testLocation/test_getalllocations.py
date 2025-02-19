from app.models.v1 import Location
from app.extensions import db


def test_get_all_locations_success(user_client):
    """Test retrieving all locations when data exists"""
    client, headers = user_client
    locations = Location.query.all()
    response = client.get("/locations", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "locations" in data
    assert isinstance(data["locations"], list)
    assert len(data["locations"]) == len(locations)
    assert any(loc["name"] == "Plant" for loc in data["locations"])


def test_get_all_locations_empty(user_client):
    """Test retrieving locations when no data exists"""
    client, headers = user_client
    db.session.query(Location).delete()
    db.session.commit()
    response = client.get("/locations", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert "locations" in data
    assert data["locations"] == []


def test_get_all_locations_unauthorized(client):
    """Test unauthorized request (No JWT)"""
    response = client.get("/locations")
    assert response.status_code == 401


def test_get_all_locations_db_error(user_client, mocker):
    """Test database failure handling"""
    client, headers = user_client
    mocker.patch.object(
        Location, "query",
        new_callable=mocker.PropertyMock,
        side_effect=Exception("DB error"))
    response = client.get("/locations", headers=headers)
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "An unexpected error occurred: DB error" in data["error"]
