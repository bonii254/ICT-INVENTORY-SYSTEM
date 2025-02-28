def test_create_alc_success(user_client):
    """Test successfully creating an asset lifecycle record"""
    client, headers = user_client
    payload = {
        "asset_id": 1,
        "event": "Maintenance",
        "notes": "Routine check completed"
    }
    response = client.post(
        "/register/assetlifecycle", headers=headers, json=payload)
    assert response.status_code == 201
    assert "AssetLifeCycle created successfully" in response.json["message"]


def test_create_alc_missing_required_fields(user_client):
    """Test creating an asset lifecycle record with missing required fields"""
    client, headers = user_client
    payload = {"event": "Disposed"}
    response = client.post(
        "/register/assetlifecycle", headers=headers, json=payload)
    assert response.status_code == 400
    assert "asset_id" in response.json["error"]


def test_create_alc_invalid_data_types(user_client):
    """Test creating an asset lifecycle record with invalid data types"""
    client, headers = user_client
    payload = {
        "asset_id": "invalid_id",
        "event": 123,
        "notes": ["Invalid note format"]
    }
    response = client.post(
        "/register/assetlifecycle", headers=headers, json=payload)
    assert response.status_code == 400
    assert "asset_id" in response.json["error"]
    assert "event" in response.json["error"]


def test_create_alc_unauthorized(client):
    """Test creating an asset lifecycle record without JWT token"""
    payload = {
        "asset_id": 2,
        "event": "Transfer",
        "notes": "Asset moved to a different location"
    }
    response = client.post("/register/assetlifecycle", json=payload)
    assert response.status_code == 401


def test_create_alc_invalid_content_type(user_client):
    """Test creating an asset lifecycle record with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "asset_id": 3,
        "event": "Repair",
        "notes": "Replaced damaged parts"
    }
    response = client.post(
        "/register/assetlifecycle", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_create_alc_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during asset lifecycle creation
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    payload = {
        "asset_id": 1,
        "event": "Inspection",
        "notes": "Regular quality check"
    }
    response = client.post(
        "/register/assetlifecycle", headers=headers, json=payload)
    print(response.json)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
