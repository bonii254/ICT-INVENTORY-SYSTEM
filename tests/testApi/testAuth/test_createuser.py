def test_valid_registration(client, app):
    """Test a successful user registration."""
    response_dept = client.post("/register/department", json={"name": "ICT1"})
    response_role = client.post("/register/role", json={
        "name": "admin1",
        "permissions": "create,read,update,delete,approve"
    })

    assert response_dept.status_code == 201, "Department creation failed"
    assert response_role.status_code == 201, "Role creation failed"

    with app.app_context():
        from app.models.v1 import db, Department, Role
        db.session.commit()

        dept = Department.query.filter_by(name="ICT1").first()
        role = Role.query.filter(Role.name.ilike(f"%admin1%")).first()

        print("All Roles in DB:", Role.query.all())
        print("Fetched Department:", dept)
        print("Fetched Role:", role)

        assert dept is not None, "Department not created"
        assert role is not None, "Role not created"


def test_registration_without_json(client):
    """Test user registration without a JSON request body."""
    response = client.post("/auth/register", data="")
    assert response.status_code == 415
    assert "Unsupported Media Type" in response.get_json()["error"]


def test_registration_with_invalid_data(client):
    """Test user registration with missing required fields."""
    user_data = {
        "email": "bonnyrangi95@gmail.com"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400, "Server should reject incomplete data"
    assert "errors" in response.get_json(), "Validation error messages missing"


def test_duplicate_user_registration(client):
    """Test registering a user with an existing email."""
    user_data = {
        "email": "bonnyrangi95@gmail.com",
        "password": "S3cur3p@ss",
        "fullname": "Boniface Murangiri",
        "department_id": 1,
        "role_id": 1
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400, "Server should reject duplicate email"
    assert "Email already registered." \
        in response.get_json()["errors"]["email"]


def test_registration_with_invalid_email(client):
    """Test user registration with invalid email format."""
    user_data = {
        "email": "invalid-email",
        "password": "S3cur3p@ss",
        "fullname": "Boniface Murangiri",
        "department_id": 1,
        "role_id": 1
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Not a valid email address." \
        in response.get_json()["errors"]["email"]


def test_registration_with_invalid_department(client):
    """Test user registration with a non-existent department."""
    user_data = {
        "email": "bonnyrangi95@gmail.com",
        "password": "SecurePass123",
        "fullname": "Boniface Murangiri",
        "department_id": 99,
        "role_id": 99
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Department with id 99 does not exist." \
        in response.get_json()["errors"]["department_id"]
    assert "Role with id 99 does not exist." \
        in response.get_json()["errors"]["role_id"]


def test_database_error_handling(client, mocker):
    """Test database failure during registration"""
    mocker.patch(
        "app.extensions.db.session.commit", side_effect=Exception("DB Error"))
    user_data = {
        "email": "bonnyrangitest@gmail.com",
        "password": "S3cur3p@ss",
        "fullname": "Boniface Murangiri",
        "department_id": 1,
        "role_id": 1
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 500, "Server should handle database errors"
    assert "An unexpected error occurred" in response.get_json()["error"]
