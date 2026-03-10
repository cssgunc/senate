import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app  # your FastAPI app
from app.models import Committee, CommitteeMembership, Senator

# --- Setup in-memory database for tests ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Override get_db for tests ---
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

        # --- Create Senators ---
    s1 = Senator(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        district_id=1,
        is_active=True,
        session_number=2016,
    )

    s2 = Senator(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        headshot_url=None,
        district_id=2,
        is_active=True,
        session_number=2025
    )
    test_db.add_all([s1, s2])
    test_db.commit()

    # --- Create Committees ---
    c1 = Committee(
        name="Finance Committee",
        description="Handles budget matters",
        chair_name="John Doe",
        chair_email="john@example.com",
        chair_senator_id=s1.id,
        is_active=True
    )
    c2 = Committee(
        name="Education Committee",
        description="Handles education policy",
        chair_name="Jane Smith",
        chair_email="jane@example.com",
        chair_senator_id=s2.id,
        is_active=False
    )
    test_db.add_all([c1, c2])
    test_db.commit()

    # --- Create Memberships ---
    m1 = CommitteeMembership(
        senator_id=s1.id,
        committee_id=c1.id,
        role="Chair",
        committee=c1,
        senator=s1
        )
    m2 = CommitteeMembership(
        senator_id=s2.id,
        committee_id=c1.id,
        role="Member",
        committee=c1,
        senator=s2
        )
    test_db.add_all([m1, m2])
    test_db.commit()

    return {"senators": [s1, s2], "committees": [c1, c2], "memberships": [m1, m2]}


@pytest.fixture
def client():
    return TestClient(app)


# --- Tests ---
def test_get_committee_by_id(client, seeded_data):
    committee = seeded_data["committees"][0]

    response = client.get(f"/committees/{committee.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == committee.id
    assert data["name"] == "Finance Committee"
    assert len(data["members"]) == 2
    roles = {c["role"] for m in data["members"] for c in m["committees"]}
    assert roles == {"Chair", "Member"}

def test_get_committee_not_found(client):
    response = client.get("/committees/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Committee not found"

def test_get_all_active_committees(client, seeded_data):
    response = client.get("/committees/")
    assert response.status_code == 200

    data = response.json()
    # Only active committees
    names = [c["name"] for c in data]
    assert "Finance Committee" in names
    assert "Education Committee" not in names
