from app.models.v1 import Department
from app.extensions import db


def test_delete_department_valid(user_client):
    """Valid case: Successfully delete an existing department."""
    department = Department(name="HR")
    db.session.add(department)
    db.session.commit()
    department_id = str(department.id)

    client, headers = user_client
    response = client.delete(f"/department/{department_id}", headers=headers)
    assert response.status_code == 200
    assert "Department deleted successfully" in response.json["Message"]


def test_delete_department_invalid_id_format(user_client):
    """Invalid case: Department ID is not a valid number."""
    client, headers = user_client
    response = client.delete("/department/abc123", headers=headers)
    assert response.status_code == 400
    assert "Invalid department ID format" in response.json["Error"]


def test_delete_department_not_found(user_client):
    """Invalid case: Department does not exist."""
    client, headers = user_client
    response = client.delete("/department/9999", headers=headers)
    assert response.status_code == 404
    assert "Department with id 9999 does not exist" in response.json["Error"]


def test_delete_department_db_failure(mocker, user_client):
    """
    Test Case: Database commit failure during department deletion.
    """
    client, headers = user_client
    dept = Department.query.filter_by(name="ICT").first()
    mocker.patch.object(
        db.session, "commit", side_effect=Exception("Database commit failed"))
    response = client.delete(
        f"/department/{dept.id}", headers=headers)
    assert response.status_code == 500
    assert response.json == {
        "error": "An unexpected error occurred: Database commit failed"
    }, "Error message mismatch"
