import pytest
from flask_jwt_extended import create_access_token, create_refresh_token
from app import create_app
from app.extensions import db
from app.models.v1 import Department, Role, User, Category, Location


@pytest.fixture()
def app():
    """Setup and teardown the test app with test data."""
    app = create_app("testing")

    with app.app_context():
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
    category = Category(
        name="networking", description="All networking devices")
    user = User(
        email="bonnyrangi95@gmail.com",
        password="s3cur3p@ss??",
        fullname="Boniface Murangiri",
        department_id=1,
        role_id=1
    )

    db.session.add_all([dept, role, location, category])
    db.session.commit()
    user.department_id = dept.id
    user.role_id = role.id
    db.session.add(user)
    db.session.commit()
