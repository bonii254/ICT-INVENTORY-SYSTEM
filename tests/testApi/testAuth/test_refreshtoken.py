from flask_jwt_extended import create_refresh_token,  decode_token
from datetime import timedelta
from app.models.v1 import User
from datetime import datetime, timezone
from app.api.auth import BLACKLIST_PREFIX, redis_client


def test_valid_refresh(refresh_client):
    """Test refreshing access token with a valid refresh token."""
    client, headers = refresh_client
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 200
    assert "access_token" in response.json


def test_missing_refresh_token(refresh_client):
    """Test refreshing without providing a refresh token."""
    client, _ = refresh_client
    response = client.post("/auth/refresh")
    assert response.status_code == 401


def test_invalid_refresh_token(refresh_client):
    """Test refreshing with an invalid/malformed refresh token."""
    client, _ = refresh_client
    headers = {"Authorization": "Bearer invalid.token.string"}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 401


def test_expired_refresh_token(refresh_client, app):
    """Test refreshing with an expired refresh token."""
    client, headers = refresh_client
    with app.app_context():
        user = User.query.filter_by(email="bonnyrangi95@gmail.com").first()
        expired_refresh_token = create_refresh_token(
            identity=str(user.id), expires_delta=timedelta(seconds=-1)
        )
        headers = {"Authorization": f"Bearer {expired_refresh_token}"}
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json["msg"]


def test_access_token_instead_of_refresh(user_client):
    """
    Test refreshing while using an access token instead of a refresh token.
    """
    client, headers = user_client
    response = client.post("/auth/refresh", headers=headers)
    assert response.status_code == 401


def test_blacklisted_refresh_token(refresh_client, app):
    """Test refreshing with a revoked/blacklisted refresh token."""
    client, _ = refresh_client
    with app.app_context():
        user = User.query.filter_by(email="bonnyrangi95@gmail.com").first()
        revoked_refresh_token = create_refresh_token(identity=str(user.id))
    decoded_token = decode_token(revoked_refresh_token)
    jti = decoded_token["jti"]
    exp_timestamp = decoded_token["exp"]
    now = int(datetime.now(timezone.utc).timestamp())
    ttl = exp_timestamp - now
    redis_client.setex(f"{BLACKLIST_PREFIX}refresh_{jti}", ttl, "revoked")
    headers = {"Authorization": f"Bearer {revoked_refresh_token}"}
    response = client.post("/auth/refresh", headers=headers)
    print(response.json)
    assert response.status_code == 401
    assert "Token has been revoked" in response.json["msg"]
