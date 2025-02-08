import pytest
from app import create_app
from app.extensions import db


@pytest.fixture()
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()

    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def clean_db(app):
    """Ensure database is clean before each test."""
    with app.app_context():
        from app.models.v1 import User, Department, Role
        db.session.execute("DELETE FROM user")  # ✅ Force delete
        db.session.execute("DELETE FROM department")
        db.session.execute("DELETE FROM role")
        db.session.commit()
