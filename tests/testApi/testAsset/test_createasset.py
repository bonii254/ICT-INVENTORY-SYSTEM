def test_create_asset(asset_user_client):
    """Test successful asset creation."""
    client, headers, asset_info = asset_user_client
    response = client.post("/register/asset", json=asset_info, headers=headers)
    assert response.status_code == 201


def test_create_asset_missing_fields(asset_user_client):
    client, headers, _ = asset_user_client
    response = client.post(
        "/register/asset",
        json={"category_id": 1, "location_id": 1}, headers=headers)
    print("Response Status:", response.status_code)
    print("Response Data:", response.get_json())
    assert response.status_code == 400


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


def test_create_asset_unexpected_error(asset_user_client, mocker):
    client, headers, asset_info = asset_user_client
    mocker.patch("app.db.session.commit", side_effect=Exception("DB Error"))
    response = client.post("/register/asset", json=asset_info, headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.get_json()["error"]


def test_create_asset_invalid_mac_address_format(asset_user_client):
    """Test invalid MAC address format"""
    client, headers, asset_info = asset_user_client
    asset_info["mac_address"] = "ZZ:ZZ:ZZ:ZZ:ZZ:ZZ"
    response = client.post("/register/asset",
                           json=asset_info,
                           headers=headers)
    assert response.status_code == 400
    assert "The MAC address 'ZZ:ZZ:ZZ:ZZ:ZZ:ZZ' is not valid." \
        in response.get_json()["error"]["mac_address"]


def test_create_asset_no_mac_address_format(asset_user_client):
    """Test None MAC address"""
    client, headers, asset_info = asset_user_client
    asset_info["mac_address"] = None
    response = client.post("/register/asset",
                           json=asset_info,
                           headers=headers)
    assert response.status_code == 201


def test_create_asset_invalid_assigned_to(asset_user_client):
    """Test assigning asset to a non-existent user"""
    client, headers, asset_info = asset_user_client
    asset_info["assigned_to"] = 9999
    response = client.post("/register/asset",
                           json=asset_info,
                           headers=headers)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_asset_invalid_category(asset_user_client):
    """Test invalid category_id"""
    client, headers, asset_info = asset_user_client
    asset_info["category_id"] = 9999
    response = client.post("/register/asset",
                           json=asset_info,
                           headers=headers)
    assert response.status_code == 400
    assert "error" in response.get_json()
