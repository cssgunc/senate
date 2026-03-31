import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Committee, CommitteeMembership, Leadership, Senator

# --- Setup shared in-memory database ---
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Override FastAPI get_db dependency ---
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
    """Create all tables once per test module."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """FastAPI TestClient using the test_db."""
    return TestClient(app)


@pytest.fixture
def seeded_committees(test_db):
    """Seed test data for committees, senators, and memberships."""
    # --- Senators ---
    s1 = Senator(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        district=1,
        is_active=True,
        session_number=2016,
    )
    s2 = Senator(
        first_name="Jane",
        last_name="Doe",
        email="jane@example.com",
        headshot_url=None,
        district=2,
        is_active=True,
        session_number=2025,
    )
    test_db.add_all([s1, s2])
    test_db.commit()

    # --- Committees ---
    c1 = Committee(
        name="Finance Committee",
        description="Handles budget matters",
        chair_name="John Doe",
        chair_email="john@example.com",
        chair_senator_id=s1.id,
        is_active=True,
    )
    c2 = Committee(
        name="Education Committee",
        description="Handles education policy",
        chair_name="Jane Smith",
        chair_email="jane@example.com",
        chair_senator_id=s2.id,
        is_active=False,
    )
    test_db.add_all([c1, c2])
    test_db.commit()

    # --- Memberships ---
    m1 = CommitteeMembership(senator_id=s1.id, committee_id=c1.id, role="Chair")
    m2 = CommitteeMembership(senator_id=s2.id, committee_id=c1.id, role="Member")
    test_db.add_all([m1, m2])
    test_db.commit()

    yield {"senators": [s1, s2], "committees": [c1, c2], "memberships": [m1, m2]}


@pytest.fixture
def seeded_leadership(test_db):
    """Seed test data for leadership."""
    l1 = Leadership(
        title="Speaker",
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        headshot_url=None,
        is_active=True,
        session_number=2025,
    )
    l2 = Leadership(
        title="Minority Leader",
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
        headshot_url=None,
        is_active=False,
        session_number=2023,
    )
    l3 = Leadership(
        title="Whip",
        first_name="Alice",
        last_name="Brown",
        email="alice@example.com",
        headshot_url=None,
        is_active=True,
        session_number=2025,
    )

    test_db.add_all([l1, l2, l3])
    test_db.commit()

    yield {"records": [l1, l2, l3]}
