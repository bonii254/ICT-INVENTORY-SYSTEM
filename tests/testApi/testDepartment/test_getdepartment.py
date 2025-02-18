from app.models.v1 import Department


def test_valid_existing_department(user_client):
    """Valid department ID should return 200."""
    client, headers = user_client
    dept = Department.query.filter_by(name="ICT").first()
    response = client.get(f'/department/{dept.id}', headers=headers)
    assert response.status_code == 200


def test_valid_non_existing_department(user_client):
    """Valid but non-existing ID should return 404."""
    client, headers = user_client
    response = client.get('/department/9999', headers=headers)
    assert response.status_code == 404
    assert "Department with id 9999 doesnot exist" \
        in response.get_json()["Error"]


def test_non_numeric_department_id(user_client):
    """Non-numeric ID should return 400."""
    client, headers = user_client
    response = client.get("/department/abc", headers=headers)
    response.status_code == 400
    assert "Invalid department ID format" in response.get_json()["Error"]


def test_negative_department_id(user_client):
    """Negative ID should return 400."""
    client, headers = user_client
    response = client.get("/department/-1", headers=headers)
    assert response.status_code == 400
    assert "Invalid department ID format" in response.get_json()["Error"]


def test_floating_point_department_id(user_client):
    """Floating-point ID should return 400."""
    client, headers = user_client
    response = client.get("/department/1.5", headers=headers)
    assert response.status_code == 400
    assert "Invalid department ID format" in response.get_json()["Error"]


def test_large_numeric_id(user_client):
    """Large out-of-range ID should return 404."""
    client, headers = user_client
    response = client.get(f"/department/{9**9}", headers=headers)
    assert response.status_code == 404
    assert "Department with id 387420489 doesnot exist" \
        in response.get_json()["Error"]


def test_department_id_with_leading_zeros(user_client):
    """ID with leading zeros should be treated correctly."""
    client, headers = user_client
    dept = Department.query.filter_by(name="ICT").first()
    response = client.get(f'/department/{000}{dept.id}', headers=headers)
    assert response.status_code == 200


def test_sql_injection_attempt(user_client):
    """SQL Injection attempt should return 400."""
    client, headers = user_client
    response = client.get("/department/1 OR 1=1", headers=headers)
    assert response.status_code == 400
    assert "Invalid department ID format" in response.get_json()["Error"]


def test_empty_department_id(user_client):
    """Empty department ID should return 404."""
    client, headers = user_client
    response = client.get("/department/", headers=headers)
    assert response.status_code == 404


def test_database_error_handling(user_client, mocker):
    """Test database failure during detting department"""
    client, headers = user_client
    mocker.patch(
        "app.extensions.db.session.get", side_effect=Exception("DB Error"))
    dept = Department.query.filter_by(name="ICT").first()
    response = client.get(f'/department/{dept.id}', headers=headers)
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json["error"]
