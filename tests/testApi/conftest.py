import pytest
from flask_jwt_extended import create_access_token, create_refresh_token
from app import create_app
from app.extensions import db
from app.models.v1 import Department, Role, User


@pytest.fixture()
def app():
    """Setup and teardown the test app with test data."""
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        dept = Department(name="ICT")
        db.session.add(dept)
        db.session.commit()

        role = Role(
            name="admin",
            permissions="create,read,update,delete,approve"
        )
        db.session.add(role)
        db.session.commit()

        user = User(
            email="bonnyrangi95@gmail.com",
            password="s3cur3p@ss??",
            fullname="Boniface Murangiri",
            department_id=dept.id,
            role_id=role.id
        )
        db.session.add(user)
        db.session.commit()

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
