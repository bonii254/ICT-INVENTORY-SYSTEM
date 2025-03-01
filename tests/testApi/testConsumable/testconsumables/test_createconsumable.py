def test_register_consumable_success(user_client):
    """Test successfully registering a consumable"""
    client, headers = user_client
    payload = {
        "name": "Printer Ink",
        "category": "Office Supplies",
        "brand": "HP",
        "model": "123XL",
        "quantity": 50,
        "unit_of_measure": "Cartridge",
        "reorder_level": 5
    }
    response = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response.status_code == 201
    assert "Consumable created successfully." in response.json["message"]
    assert response.json["Printer Ink"]["category"] == "Office Supplies"


def test_register_consumable_missing_required_fields(user_client):
    """Test registering a consumable with missing required fields"""
    client, headers = user_client
    payload = {"name": "Paper"}
    response = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response.status_code == 400
    assert "category" in response.json["error"]


def test_register_consumable_invalid_data_types(user_client):
    """Test registering a consumable with incorrect data types"""
    client, headers = user_client
    payload = {
        "name": 123,
        "category": "Office Supplies",
        "brand": "HP",
        "model": 456,
        "quantity": "fifty",
        "unit_of_measure": "Cartridge",
        "reorder_level": "ten"
    }
    response = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response.status_code == 400


def test_register_consumable_unauthorized(client):
    """Test registering a consumable without JWT token"""
    payload = {
        "name": "Stapler",
        "category": "Office Supplies",
        "brand": "Swingline",
        "model": "747",
        "quantity": 20,
        "unit_of_measure": "Piece",
        "reorder_level": 3
    }
    response = client.post("/register/consumable", json=payload)
    assert response.status_code == 401


def test_register_consumable_invalid_content_type(user_client):
    """Test registering a consumable with invalid Content-Type"""
    client, headers = user_client
    payload = {
        "name": "Markers",
        "category": "Stationery",
        "brand": "Expo",
        "model": "Dry Erase",
        "quantity": 30,
        "unit_of_measure": "Set",
        "reorder_level": 5
    }
    response = client.post(
        "/register/consumable", headers=headers, data=payload)
    assert response.status_code == 415
    assert "Content-Type must be application/json" in response.json["error"]


def test_register_consumable_negative_quantity(user_client):
    """Test registering a consumable with a negative quantity"""
    client, headers = user_client
    payload = {
        "name": "Toner Cartridge",
        "category": "Office Supplies",
        "brand": "Canon",
        "model": "456X",
        "quantity": -10,
        "unit_of_measure": "Cartridge",
        "reorder_level": 2
    }
    response = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response.status_code == 400
    assert "quantity" in response.json["error"]


def test_register_consumable_duplicate_entry(user_client, app):
    """Test registering a duplicate consumable entry"""
    client, headers = user_client
    payload = {
        "name": "Scissors",
        "category": "Office Tools",
        "brand": "Fiskars",
        "model": "SharpEdge",
        "quantity": 10,
        "unit_of_measure": "Piece",
        "reorder_level": 1
    }
    response1 = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response1.status_code == 201
    response2 = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response2.status_code == 400


def test_register_consumable_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during consumable registration
    """
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB error"))
    payload = {
        "name": "Binder Clips",
        "category": "Stationery",
        "brand": "Staples",
        "model": "Medium",
        "quantity": 25,
        "unit_of_measure": "Box",
        "reorder_level": 5
    }
    response = client.post(
        "/register/consumable", headers=headers, json=payload)
    assert response.status_code == 500
    assert "An unexpected error occured" in response.json["error"]
