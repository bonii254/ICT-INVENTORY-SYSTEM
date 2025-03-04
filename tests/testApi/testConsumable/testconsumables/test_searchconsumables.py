from app.models.v1 import Consumables
from app.extensions import db
import pytest


def test_search_consumables_by_name(user_client):
    """Test searching for consumables by name"""
    client, headers = user_client
    response = client.get("/consumables/search?name=Solid State Drive5 (SSD)",
                          headers=headers)
    assert response.status_code == 200
    assert len(response.json["consumables"]) > 0


def test_search_consumables_by_category(user_client):
    """Test searching for consumables by category"""
    client, headers = user_client
    response = client.get(
        "/consumables/search?category=Storage Devices",
        headers=headers)
    assert response.status_code == 200
    assert len(response.json["consumables"]) > 0


def test_search_consumables_by_brand(user_client):
    """Test searching for consumables by brand"""
    client, headers = user_client
    response = client.get(
        "/consumables/search?brand=Samsung",
        headers=headers
    )
    assert response.status_code == 200
    assert len(response.json["consumables"]) > 0


def test_search_consumables_multiple_filters(user_client, app):
    """Test searching with multiple filters"""
    client, headers = user_client
    response = client.get(
        "/consumables/search?brand=Samsung&category=Storage Devices",
        headers=headers)
    assert response.status_code == 200
    assert len(response.json["consumables"]) > 0


def test_search_consumables_no_results(user_client):
    """Test searching for a consumable that does not exist"""
    client, headers = user_client
    response = client.get(
        "/consumables/search?name=NonExistent",
        headers=headers)
    assert response.status_code == 200
    assert response.json["consumables"] == []


def test_search_consumables_no_filters(user_client, app):
    """Test searching with no filters (should return all consumables)"""
    client, headers = user_client
    response = client.get("/consumables/search", headers=headers)
    assert response.status_code == 200
    assert len(response.json["consumables"]) > 0


def test_search_consumables_invalid_method(user_client):
    """
    Test accessing search endpoint with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/consumables/search", headers=headers)
    assert response.status_code == 405


def test_search_consumables_unauthorized(client):
    """Test searching for consumables without authentication"""
    response = client.get("/consumables/search")
    assert response.status_code == 401
