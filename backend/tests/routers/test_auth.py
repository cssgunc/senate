from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import ACCESS_TOKEN_EXPIRE_HOURS, JWT_ALGORITHM, JWT_SECRET

# -----------------------------
# Tests
# -----------------------------


def test_dev_login_known_onyen(client, seeded_admins):
    response = client.post("/api/auth/dev-login", json={"onyen": "user123456789"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_dev_login_unknown_onyen(client, seeded_admins):
    response = client.post("/api/auth/dev-login", json={"onyen": "notexist"})
    assert response.status_code == 401


def test_dev_login_disabled_in_production(client, seeded_admins, monkeypatch):
    monkeypatch.setattr("app.routers.auth.ENVIRONMENT", "production")
    response = client.post("/api/auth/dev-login", json={"onyen": "user123456789"})
    assert response.status_code == 404


def test_me_endpoint_with_valid_token(client, seeded_admins):
    login = client.post("/api/auth/dev-login", json={"onyen": "user123456789"})
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
    # log in as a normal (staff) user
    login = client.post("/api/auth/dev-login", json={"onyen": "user987654321"})
    token = login.json()["access_token"]

    # access an admin-only route
    response = client.get("/api/auth/admin-only", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403

    # access with admin token
    login_admin = client.post("/api/auth/dev-login", json={"onyen": "user123456789"})
    admin_token = login_admin.json()["access_token"]
    response2 = client.get(
        "/api/auth/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response2.status_code == 200


def test_saml_login_unconfigured_returns_503(client):
    response = client.get("/api/auth/saml/login", follow_redirects=False)
    assert response.status_code == 503


def test_saml_acs_unconfigured_returns_503(client):
    response = client.post("/api/auth/saml/acs")
    assert response.status_code == 503
