import pytest


def test_generate_software_report_success(user_client):
    """
    Test successfully generating a software report without filters
    """
    client, headers = user_client
    response = client.get("/software/report", headers=headers)
    assert response.status_code == 200
    assert "Report" in response.json
    assert isinstance(response.json["Report"], list)


def test_generate_software_report_filter_by_name(user_client):
    """
    Test generating a software report filtered by software name
    """
    client, headers = user_client
    response = client.get("/software/report?name=Bitdefender Total Security",
                          headers=headers)
    assert response.status_code == 200


def test_generate_software_report_expired_only(user_client):
    """
    Test generating a software report with expired software only
    """
    client, headers = user_client
    response = client.get(
        "/software/report?expired_only=true", headers=headers)
    assert response.status_code == 200


def test_generate_software_report_valid_date_range(user_client):
    """
    Test generating a software report within a valid date range
    """
    client, headers = user_client
    start_date = "2024-01-01"
    end_date = "2027-12-31"
    response = client.get(
        f"/software/report?start_date={start_date}&end_date={end_date}",
        headers=headers)
    assert response.status_code == 200


def test_generate_software_report_invalid_date_range(user_client):
    """
    Test handling when start_date is greater than end_date
    """
    client, headers = user_client
    response = client.get(
        "/software/report?start_date=2025-12-31&end_date=2024-01-01",
        headers=headers)
    assert response.status_code == 400


def test_generate_software_report_missing_dates(user_client):
    """
    Test handling when either start_date or end_date is missing
    """
    client, headers = user_client
    response1 = client.get(
        "/software/report?start_date=2025-01-01", headers=headers)
    assert response1.status_code == 400
    response2 = client.get("/software/report?end_date=2025-12-31",
                           headers=headers)
    assert response2.status_code == 400


def test_generate_software_report_invalid_date_format(user_client):
    """
    Test handling of invalid date format in query parameters
    """
    client, headers = user_client
    response = client.get(
        "/software/report?start_date=2024/01/01&end_date=2025/12/31",
        headers=headers)
    assert response.status_code == 400


def test_generate_software_report_unauthorized(client):
    """
    Test generating a software report without JWT token
    """
    response = client.get("/software/report")
    assert response.status_code == 401


def test_generate_software_report_invalid_method(user_client):
    """
    Test accessing the report endpoint with an unsupported HTTP method (POST)
    """
    client, headers = user_client
    response = client.post("/software/report", headers=headers)
    assert response.status_code == 405


@pytest.mark.xfail(reason="Mocking error")
def test_generate_software_report_internal_server_error(user_client, mocker):
    """
    Test handling of unexpected server error during report generation
    """
    client, headers = user_client
    mocker.patch(
        "app.models.v1.Software.query.all",
        side_effect=Exception("DB error"))
    response = client.get("/software/report", headers=headers)
    assert response.status_code == 500
