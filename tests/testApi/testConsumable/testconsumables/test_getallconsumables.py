from app.models.v1 import Consumables
from app.extensions import db


def test_get_all_consumables_success(user_client, app):
    """Test retrieving all consumables successfully when records exist"""
    client, headers = user_client
    with app.app_context():
        consumable = Consumables(name="Paper", category="Office Supplies",
                                 brand="Xerox", model="A4", quantity=100,
                                 unit_of_measure="Ream", reorder_level=10)
        db.session.add(consumable)
        db.session.commit()

    response = client.get("/consumables", headers=headers)
    assert response.status_code == 200
    assert "consumables" in response.json
    assert isinstance(response.json["consumables"], list)
    assert len(response.json["consumables"]) > 0


def test_get_all_consumables_no_data(user_client, app):
    """Test retrieving all consumables when no records exist"""
    client, headers = user_client
    with app.app_context():
        db.session.query(Consumables).delete()
        db.session.commit()

    response = client.get("/consumables", headers=headers)
    assert response.status_code == 404
    assert response.json["error"] == "No consumable found"


def test_get_all_consumables_unauthorized(client):
    """Test retrieving all consumables without authentication"""
    response = client.get("/consumables")
    assert response.status_code == 401


def test_get_all_consumables_invalid_method(user_client):
    """Test accessing the endpoint with an unsupported HTTP method (POST)"""
    client, headers = user_client
    response = client.post("/consumables", headers=headers)
    assert response.status_code == 405


def test_get_all_consumables_internal_server_error(user_client, mocker):
    """Test handling of unexpected server error during retrieval"""
    client, headers = user_client
    mocker.patch.object(
       Consumables, "query",
       new_callable=mocker.PropertyMock,
       side_effect=Exception("DB error"))
    response = client.get("/consumables", headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occured: DB error" in response.json["error"]
