def test_update_asset_transfer_not_found(user_client):
    """Test updating a non-existent asset transfer"""
    client, headers = user_client
    payload = {"to_location_id": 2}
    response = client.put(
        "/assettransfer/999", headers=headers, json=payload)
    assert response.status_code == 404
    assert response.json["error"] == "Asset transfer not found"


def test_update_asset_transfer_invalid_data(user_client):
    """Test updating asset transfer with invalid data"""
    client, headers = user_client
    payload = {"to_location_id": "invalid"}
    response = client.put(
        "/assettransfer/1",
        headers=headers,
        json=payload)
    assert response.status_code == 400


def test_update_asset_transfer_invalid_content_type(user_client):
    """Test updating asset transfer with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "to_location_id": 2,
        "transferred_to": 3
    }
    response = client.put(
        "/assettransfer/1", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_update_asset_transfer_unauthorized(client):
    """Test updating asset transfer without JWT token"""
    response = client.put("/assettransfer/1", json={"to_location_id": 2})
    assert response.status_code == 401


def test_update_asset_transfer_invalid_method(user_client):
    """Test accessing asset transfer update
    with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/assettransfer/1", headers=headers)
    assert response.status_code == 405
