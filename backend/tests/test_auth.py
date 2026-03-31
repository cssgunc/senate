import re
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import ACCESS_TOKEN_EXPIRE_HOURS, JWT_ALGORITHM, JWT_SECRET
from app.database import Base, get_db
from app.main import app
from app.models import Admin

# -----------------------------
# Setup in-memory test database
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -----------------------------
# Adds REGEXP support for SQLite
# -----------------------------
@event.listens_for(Engine, "connect")
def sqlite_regexp(dbapi_connection, connection_record):
    def regexp(expr, item):
        if item is None:
            return False
        return bool(re.fullmatch(expr, str(item)))

    dbapi_connection.create_function("REGEXP", 2, regexp)


# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables and test users
Base.metadata.create_all(bind=engine)

# Seed a test user
db = TestingSessionLocal()

test_admin = Admin(
    id=1,
    email="admin@test.com",
    first_name="Admin",
    last_name="Tester",
    pid="123456789",
    role="admin",
)

test_user = Admin(
    id=2,
    email="user@test.com",
    first_name="Normal",
    last_name="User",
    pid="987654321",
    role="staff",
)

db.add_all([test_admin, test_user])
db.commit()
db.close()

client = TestClient(app)

# -----------------------------
# Tests
# -----------------------------


def test_valid_login():
    response = client.post(
        "/api/auth/login", params={"email": "admin@test.com", "pid": "123456789"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_credentials():
    response = client.post("/api/auth/login", params={"email": "admin@test.com", "pid": "wrong"})
    assert response.status_code == 401

    response2 = client.post(
        "/api/auth/login", params={"email": "notexist@test.com", "pid": "123456789"}
    )
    assert response2.status_code == 401


def test_me_endpoint_with_valid_token():
    login = client.post("/api/auth/login", params={"email": "admin@test.com", "pid": "123456789"})
    token = login.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


def test_expired_token():
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


def test_role_check():
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
