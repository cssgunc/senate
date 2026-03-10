import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


from app.database import Base, get_db
from app.main import app  # your FastAPI app
from app.models import Leadership

# --- Setup in-memory SQLite for tests ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Override get_db for testing ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# --- Fixtures ---
@pytest.fixture(scope="module")
def test_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def seeded_data(test_db):
    # Seed Leadership records
    l1 = Leadership(
        title="Speaker",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        is_active=True,
        session_number=2025
    )
    l2 = Leadership(
        title="Minority Leader",
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        headshot_url=None,
        is_active=False,
        session_number=2023
    )
    l3 = Leadership(
        title="Whip",
        first_name="Alice",
        last_name="Brown",
        email="alice@example.com",
        headshot_url=None,
        is_active=True,
        session_number=2025
    )

    test_db.add_all([l1, l2, l3])
    test_db.commit()

    return {"records": [l1, l2, l3]}

@pytest.fixture
def client():
    return TestClient(app)

# --- Tests ---
def test_get_all_active_leadership(client, seeded_data):
    response = client.get("/leadership/")
    assert response.status_code == 200
    data = response.json()

    # Only active records should be returned
    titles = [l["title"] for l in data]
    assert "Speaker" in titles
    assert "Whip" in titles
    assert "Minority Leader" not in titles

def test_get_leadership_by_session_number(client, seeded_data):
    response = client.get("/leadership/?session_number=2025")
    assert response.status_code == 200
    data = response.json()

    # Should return only records with session_number=2025
    assert all(l["session_number"] == 2025 for l in data)
    titles = [l["title"] for l in data]
    assert set(titles) == {"Speaker", "Whip"}

def test_get_leadership_by_id_success(client, seeded_data):
    leadership = seeded_data["records"][0]  # Speaker
    response = client.get(f"/leadership/{leadership.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == leadership.id
    assert data["title"] == leadership.title

def test_get_leadership_by_id_not_found(client):
    response = client.get("/leadership/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Leadership record not found"