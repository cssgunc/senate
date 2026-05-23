from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

import app.routers.auth as auth_router
from app.config import ACCESS_TOKEN_EXPIRE_HOURS, JWT_ALGORITHM, JWT_SECRET

# -----------------------------
# Tests
# -----------------------------


@pytest.fixture(autouse=True)
def clear_login_rate_limits():
    auth_router.failed_login_attempts.clear()
    yield
    auth_router.failed_login_attempts.clear()


def test_valid_login(client, seeded_admins):
    response = client.post(
        "/api/auth/login", json={"onyen": "user123456789", "password": "TestPassword123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_credentials(client, seeded_admins):
    response = client.post(
        "/api/auth/login", json={"onyen": "user123456789", "password": "WrongPassword123!"}
    )
    assert response.status_code == 401

    response2 = client.post(
        "/api/auth/login", json={"onyen": "notexist", "password": "TestPassword123!"}
    )
    assert response2.status_code == 401


def test_me_endpoint_with_valid_token(client, seeded_admins):
    login = client.post(
        "/api/auth/login", json={"onyen": "user123456789", "password": "TestPassword123!"}
    )
    token = login.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


def test_expired_token(client, seeded_admins):
    expired_token = jwt.encode(
        {
            "sub": "1",
            "exp": datetime.now(timezone.utc) - timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert response.status_code == 401


def test_role_check(client, seeded_admins):
    # login as a normal user
    login = client.post(
        "/api/auth/login", json={"onyen": "user987654321", "password": "TestPassword123!"}
    )
    token = login.json()["access_token"]

    # access an admin-only route
    response = client.get("/api/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    # access with admin token
    login_admin = client.post(
        "/api/auth/login", json={"onyen": "user123456789", "password": "TestPassword123!"}
    )
    admin_token = login_admin.json()["access_token"]
    response2 = client.get(
        "/api/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response2.status_code == 200


def test_login_rejects_too_long_password(client, seeded_admins):
    response = client.post(
        "/api/auth/login", json={"onyen": "user123456789", "password": "x" * 129}
    )
    assert response.status_code == 422


def test_successful_login_clears_failed_attempts(client, seeded_admins):
    bad_payload = {"onyen": "user123456789", "password": "WrongPassword123!"}
    good_payload = {"onyen": "user123456789", "password": "TestPassword123!"}

    assert client.post("/api/auth/login", json=bad_payload).status_code == 401
    assert auth_router.failed_login_attempts

    assert client.post("/api/auth/login", json=good_payload).status_code == 200
    assert auth_router.failed_login_attempts == {}


def test_failed_login_rate_limited(client, seeded_admins):
    payload = {"onyen": "user123456789", "password": "WrongPassword123!"}

    for _ in range(auth_router.MAX_FAILED_LOGIN_ATTEMPTS):
        assert client.post("/api/auth/login", json=payload).status_code == 401

    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 429
