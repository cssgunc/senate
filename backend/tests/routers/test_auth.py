from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import ACCESS_TOKEN_EXPIRE_HOURS, JWT_ALGORITHM, JWT_SECRET

# -----------------------------
# Tests
# -----------------------------

def test_valid_login(client, seeded_admins):
    response = client.post(
        "/api/auth/login", params={"email": "admin@test.com", "pid": "123456789"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_credentials(client, seeded_admins):
    response = client.post("/api/auth/login", params={"email": "admin@test.com", "pid": "wrong"})
    assert response.status_code == 401

    response2 = client.post(
        "/api/auth/login", params={"email": "notexist@test.com", "pid": "123456789"}
    )
    assert response2.status_code == 401


def test_me_endpoint_with_valid_token(client, seeded_admins):
    login = client.post("/api/auth/login", params={"email": "admin@test.com", "pid": "123456789"})
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
    login = client.post("/api/auth/login", params={"email": "user@test.com", "pid": "987654321"})
    token = login.json()["access_token"]

    # access an admin-only route
    response = client.get("/api/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    # access with admin token
    login_admin = client.post(
        "/api/auth/login", params={"email": "admin@test.com", "pid": "123456789"}
    )
    admin_token = login_admin.json()["access_token"]
    response2 = client.get(
        "/api/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response2.status_code == 200
