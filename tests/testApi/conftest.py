import pytest
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token
from app import create_app
from app.extensions import db
from app.models.v1 import (
    Department, Role, User, Category, Location, Asset, Status, AssetTransfer,
    Ticket, Software, AssetLifecycle, Consumables, StockTransaction)


@pytest.fixture()
def app():
    """Setup and teardown the test app with test data."""
    app = create_app("testing")

    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_test_data()
    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_client(client, app):
    """Returns a client with an authenticated user (JWT)."""
    with app.app_context():
        user = User.query.filter_by(email="bonnyrangi95@gmail.com").first()
        access_token = create_access_token(identity=str(user.id))

    return client, {"Authorization": f"Bearer {access_token}"}


@pytest.fixture()
def asset_user_client(user_client, app):
    """Returns a client with asset data."""
    client, headers = user_client

    with app.app_context():
        dept = Department.query.first()
        user = User.query.first()
        user2 = User.query.filter_by(email="vnjenga@gmail.com").first()
        category = Category.query.first()
        location = Location.query.first()
        location2 = Location.query.filter_by(name="society").first()
        status = Status.query.first()
        asset = Asset.query.first()

        assert all(
            [dept, user, user2, category, location, location2, status]
            ), "Test data is missing."

        asset_info = {
            "category_id": category.id,
            "assigned_to": user.id,
            "location_id": location.id,
            "status_id": status.id,
            "purchase_date": "2025-01-01",
            "warranty_expiry": "2026-01-01",
            "configuration": "Intel i7, 16GB RAM, 512GB SSD, Windows 11",
            "department_id": dept.id,
            "ip_address": "192.168.37.15",
            "mac_address": "11:1A:2B:3C:6D:7E"
        }
        assettransfer_info = {
            "asset_id": asset.id,
            "to_location_id": location2.id,
            "transferred_to": user2.id,
            "notes": "test transfer"
        }

    return client, headers, asset_info, assettransfer_info


@pytest.fixture()
def refresh_client(client, app):
    """refreshing access token."""
    with app.app_context():
        user = User.query.filter_by(email="bonnyrangi95@gmail.com").first()
        refresh_token = create_refresh_token(identity=str(user.id))

    return client, {"Authorization": f"Bearer {refresh_token}"}


def seed_test_data():
    """Helper function to seed test data into the database."""
    dept = Department(name="ICT")
    role = Role(name="admin", permissions="create,read,update,delete,approve")
    location = Location(name="Plant", address="Githunguri")
    location2 = Location(name="society", address="Githunguri")
    category = Category(
        name="Computers:Desktop", description="All networking devices")
    status = Status(
        name="new", description="Newly purchased and not yet deployed.")
    software = Software(name="Bitdefender Total Security", version="26.0",
                        license_key="BDTS-XXXXX-XXXXX-XXXXX-XXXXX",
                        expiry_date=datetime.strptime(
                            "2026-01-01", "%Y-%m-%d").date())
    software2 = Software(name="Photoshop", version="26.0",
                        license_key="BDTS-XXXXX-KKKKK-XXXXX-XXXXX",
                        expiry_date=datetime.strptime(
                            "2025-01-01", "%Y-%m-%d").date())
    consumable = Consumables(
        name="Solid State Drive5 (SSD)",
        category="Storage Devices",
        brand="Samsung",
        quantity=12,
        model="870 EVO 1TB",
        unit_of_measure="Piece",
        reorder_level=10
    )

    db.session.add_all([dept, role, location2, location, category, status,
                        software, software2, consumable])
    db.session.commit()

    user = User(
        email="bonnyrangi95@gmail.com",
        password="s3cur3p@ss??",
        fullname="Boniface Murangiri",
        department_id=dept.id,
        role_id=role.id
    )
    user2 = User(
        email="vnjenga@gmail.com",
        password="s3cur3p@ss??",
        fullname="vincent Njenga",
        department_id=dept.id,
        role_id=role.id
    )
    db.session.add_all([user, user2])
    db.session.commit()

    asset = Asset(
        asset_tag="ASSET-001",
        name="Laptop",
        category_id=category.id,
        assigned_to=user.id,
        location_id=location.id,
        status_id=status.id,
        purchase_date=datetime.strptime("2023-01-01", "%Y-%m-%d").date(),
        warranty_expiry=datetime.strptime("2026-01-01", "%Y-%m-%d").date(),
        configuration="Intel i7, 16GB RAM, 512GB SSD, Windows 11",
        department_id=dept.id,
        serial_number="192.168.37.145",
        model_number="01:1A:2B:3C:6D:7E"
    )

    db.session.add(asset)
    db.session.commit()
    assettransfer = AssetTransfer(
        asset_id=asset.id,
        from_location_id=location.id,
        to_location_id=location2.id,
        transferred_from=user.id,
        transferred_to=user2.id,
        notes="test transfer"
    )
    db.session.add(assettransfer)
    db.session.commit()
    ticket = Ticket(
        asset_id = asset.id,
        user_id = user.id,
        status = "Open",
        description = "The asset is malfunctioning",
        resolution_notes = "Pending diagnostics and repair."
    )
    db.session.add(ticket)
    db.session.commit()
    assetlifecycle = AssetLifecycle(
        asset_id=asset.id,
        event="Maintenance",
        notes="Routine check completed")
    db.session.add(assetlifecycle)
    db.session.commit()
    transaction = StockTransaction(
        consumable_id=consumable.id,
        department_id=dept.id,
        transaction_type="IN",
        user_id=user.id,
        quantity=10
    )
    transaction2 = StockTransaction(
        consumable_id=consumable.id,
        department_id=dept.id,
        transaction_type="OUT",
        user_id=user.id,
        quantity=10
    )
    db.session.add_all([transaction, transaction2])
    db.session.commit()

