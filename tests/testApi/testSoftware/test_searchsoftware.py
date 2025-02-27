from app.models.v1 import Software
from app.extensions import db


def test_search_software_by_name(user_client, app):
    """Test searching software records by name"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"
    response = client.get(
        f"/software/search?name={software.name}", headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert any(sw["name"] ==
               software.name for sw in response.json["Softwares"])


def test_search_software_by_version(user_client, app):
    """Test searching software records by version"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"
    response = client.get(
        f"/software/search?version={software.version}", headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert any(sw["version"] ==
               software.version for sw in response.json["Softwares"])


def test_search_software_by_license_key(user_client, app):
    """Test searching software records by license key"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"
    response = client.get(
        f"/software/search?license_key={software.license_key}",
        headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert any(sw["license_key"] ==
               software.license_key for sw in response.json["Softwares"])


def test_search_software_no_results(user_client):
    """Test searching software with a query that matches no records"""
    client, headers = user_client
    response = client.get(
        "/software/search?name=NonExistentSoftware", headers=headers)
    assert response.status_code == 200
    assert response.json["Softwares"] == []


def test_search_software_multiple_filters(user_client, app):
    """Test searching software with multiple query parameters"""
    client, headers = user_client
    with app.app_context():
        software = Software.query.first()
        assert software, "No software found in database"
    response = client.get(
        f"/software/search?name={software.name}&version={software.version}",
        headers=headers)
    assert response.status_code == 200
    assert "Softwares" in response.json
    assert isinstance(response.json["Softwares"], list)
    assert any(sw["name"] == software.name and sw["version"] ==
               software.version for sw in response.json["Softwares"])


def test_search_software_unauthorized(client):
    """Test searching software records without JWT token"""
    response = client.get("/software/search?name=Adobe")
    assert response.status_code == 401


def test_search_software_invalid_method(user_client):
    """Test searching software with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/software/search", headers=headers)
    assert response.status_code == 405
