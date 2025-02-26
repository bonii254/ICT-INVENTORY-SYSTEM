def test_valid_asset_transfer(asset_user_client):
    """Test successful asset transfer with existing data."""
    client, headers, _, assettransfer_info = asset_user_client
    response = client.post("/register/assettransfer",
                           headers=headers,
                           json=assettransfer_info)
    assert response.status_code == 201
    assert response.json["message"] == "AssetTransfer registered successfully!"


def test_asset_not_found(asset_user_client):
    """Test non-existent asset ID"""
    client, headers, _, assettransfer_info = asset_user_client
    assettransfer_info['asset_id'] = 999
    response = client.post("/register/assettransfer",
                           headers=headers,
                           json=assettransfer_info)
    print("Response JSON:", response.json)
    assert response.status_code == 404
    assert response.json["error"] == "Asset not found"


def test_invalid_data_types(asset_user_client):
    """Test non-integer asset_id"""
    client, headers, _, _ = asset_user_client
    payload = {
        "asset_id": "invalid",
        "to_location_id": 4,
        "transferred_to": 5
    }
    response = client.post("/register/assettransfer",
                           headers=headers,
                           json=payload)
    assert response.status_code == 400


def test_invalid_content_type(asset_user_client):
    """Test unsupported content type"""
    client, headers, _, _ = asset_user_client
    payload = {
        "asset_id": 1,
        "to_location_id": 4,
        "transferred_to": 5
    }
    response = client.post("/register/assettransfer",
                           headers=headers,
                           data=payload)
    assert response.status_code == 415


def test_large_payload(asset_user_client):
    """Test excessively long notes field"""
    client, headers, _, _ = asset_user_client
    payload = {
        "asset_id": 1,
        "to_location_id": 4,
        "transferred_to": 5,
        "notes": "A" * 5001
    }
    response = client.post("/register/assettransfer",
                           headers=headers,
                           json=payload)
    assert response.status_code == 400
