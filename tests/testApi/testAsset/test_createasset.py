def test_create_asset(asset_user_client):
    """Test successful asset creation."""
    client, headers, asset_info = asset_user_client
    response = client.post("/register/asset", json=asset_info, headers=headers)
    assert response.status_code == 201


def test_create_asset_missing_fields(asset_user_client):
    client, headers, _ = asset_user_client
    response = client.post("/register/asset", json={"category_id": 1, "location_id": 1}, headers=headers)

    # Print response for debugging
    print("Response Status:", response.status_code)
    print("Response Data:", response.get_json())

    assert response.status_code == 400, f"Unexpected status code: {response.status_code}, Response: {response.get_data(as_text=True)}"


def test_create_asset_invalid_json(asset_user_client):
    """Test invalid JSON format"""
    client, headers, _ = asset_user_client
    response = client.post("/register/asset",
                           data="{invalid_json}",
                           headers=headers)
    assert response.status_code == 415
    assert "Unsupported Media Type: Content-Type must be application/json" \
        in response.get_json()["error"]


def test_create_asset_duplicate_entry(asset_user_client):
    """Test duplicate asset creation"""
    client, headers, asset_info = asset_user_client
    client.post("/register/asset",
                json=asset_info,
                headers=headers)
    response = client.post("/register/asset",
                           json=asset_info,
                           headers=headers)
    assert response.status_code == 400
