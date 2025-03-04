from app.models.v1 import StockTransaction, User, Department, Consumables
from app.extensions import db
import pytest
from datetime import datetime, timedelta


def test_search_transaction_success(user_client):
    """Test successful search for stock transactions with valid filters"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?transaction_type=IN", headers=headers)
    assert response.status_code == 200
    assert "transactions" in response.json


def test_search_transaction_by_fullname(user_client):
    """Test searching transactions by user's full name"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?fullname=Boniface Murangiri", headers=headers)
    assert response.status_code == 200


def test_search_transaction_by_department(user_client):
    """Test searching transactions by department name"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?department_name=ICT", headers=headers)
    assert response.status_code == 200


def test_search_transaction_by_consumable(user_client):
    """Test searching transactions by consumable name"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?consumable_name=Solid State Drive5 (SSD)",
        headers=headers)
    assert response.status_code == 200


def test_search_transaction_by_date_range(user_client):
    """Test searching transactions within a specific date range"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?start_date=2024-01-01&end_date=2024-12-31",
        headers=headers)
    assert response.status_code == 200


def test_search_transaction_invalid_date_format(user_client):
    """Test searching transactions with an invalid date format"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?start_date=01-01-2024", headers=headers)
    assert response.status_code == 400
    assert "Invalid start_date format" in response.json["error"]


def test_search_transaction_pagination(user_client):
    """Test searching transactions with pagination parameters"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?page=1&per_page=5", headers=headers)
    assert response.status_code == 200
    assert "transactions" in response.json
    assert response.json["page"] == 1
    assert response.json["per_page"] == 5


def test_search_transaction_no_results(user_client):
    """Test searching transactions that yield no results"""
    client, headers = user_client
    response = client.get(
        "/transaction/search?fullname=NonExistentUser",
        headers=headers)
    assert response.status_code == 200
    assert response.json["transactions"] == []


def test_search_transaction_invalid_method(user_client):
    """
    Test accessing the search endpoint with an invalid HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/transaction/search", headers=headers)
    assert response.status_code == 405


def test_search_transaction_unauthorized(client):
    """Test searching transactions without authentication"""
    response = client.get("/transaction/search")
    assert response.status_code == 401


def test_search_transaction_internal_server_error(user_client, mocker):
    """Test handling unexpected server errors"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.query", side_effect=Exception("DB error"))
    response = client.get(
        "/transaction/search?transaction_type=IN", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
