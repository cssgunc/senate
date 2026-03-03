"""Fixtures for route integration tests.

Uses an in-memory SQLite database so tests run without a SQL Server connection.
All GET-only endpoints are tested against seeded fixture data.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import all models so they register with Base before create_all
import app.models  # noqa: F401
from app.database import get_db
from app.main import app
from app.models import Admin, Senator
from app.models.base import Base
from app.models.cms import Committee, CommitteeMembership, News
from app.models.District import District

# ---------------------------------------------------------------------------
# Shared in-memory SQLite engine (module-scoped — created once per test module)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def test_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    @event.listens_for(engine, "connect")
    def enforce_foreign_keys(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Strip SQL Server-specific CHECK constraints before creating tables on SQLite
    for table in Base.metadata.tables.values():
        table.constraints = {
            c for c in table.constraints if not isinstance(c, CheckConstraint)
        }

    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Seed test data once per module
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def seeded_engine(test_engine):
    """Populate the test DB with representative fixture data."""
    Session = sessionmaker(bind=test_engine)
    db = Session()

    # --- Districts ---
    d1 = District(district_name="On-Campus", description="On-campus students")
    d2 = District(district_name="Off-Campus", description="Off-campus students")
    db.add_all([d1, d2])
    db.flush()

    # --- Admin (news author) ---
    admin = Admin(
        email="author@unc.edu",
        first_name="Test",
        last_name="Author",
        pid="111111111",
        role="admin",
    )
    db.add(admin)
    db.flush()

    # --- News articles ---
    published_recent = News(
        title="Recent News",
        body="Body of recent news.",
        summary="Recent summary.",
        image_url=None,
        author_id=admin.id,
        date_published=datetime(2026, 3, 3, 12, 0),
        date_last_edited=datetime(2026, 3, 3, 12, 0),
        is_published=True,
    )
    published_older = News(
        title="Older News",
        body="Body of older news.",
        summary="Older summary.",
        image_url="https://img.unc.edu/old.jpg",
        author_id=None,
        date_published=datetime(2026, 1, 1, 9, 0),
        date_last_edited=datetime(2026, 1, 1, 9, 0),
        is_published=True,
    )
    draft = News(
        title="Draft Article",
        body="Unpublished body.",
        summary="Draft summary.",
        image_url=None,
        author_id=admin.id,
        date_published=datetime(2026, 2, 1, 10, 0),
        date_last_edited=datetime(2026, 2, 1, 10, 0),
        is_published=False,
    )
    db.add_all([published_recent, published_older, draft])
    db.flush()

    # --- Committees ---
    finance = Committee(
        name="Finance Committee",
        description="Budget oversight.",
        chair_name="Finance Chair",
        chair_email="finance@unc.edu",
        is_active=True,
    )
    judiciary = Committee(
        name="Judiciary Committee",
        description="Legal matters.",
        chair_name="Judiciary Chair",
        chair_email="judiciary@unc.edu",
        is_active=True,
    )
    db.add_all([finance, judiciary])
    db.flush()

    # --- Senators (session 35 = current) ---
    s1 = Senator(
        first_name="Alice",
        last_name="Smith",
        email="asmith@unc.edu",
        district=d1.id,
        is_active=True,
        session_number=35,
    )
    s2 = Senator(
        first_name="Bob",
        last_name="Jones",
        email="bjones@unc.edu",
        district=d2.id,
        is_active=True,
        session_number=35,
    )
    s3_inactive = Senator(
        first_name="Carol",
        last_name="Lee",
        email="clee@unc.edu",
        district=d1.id,
        is_active=False,
        session_number=35,
    )
    s4_old_session = Senator(
        first_name="Dan",
        last_name="Brown",
        email="dbrown@unc.edu",
        district=d1.id,
        is_active=True,
        session_number=34,
    )
    db.add_all([s1, s2, s3_inactive, s4_old_session])
    db.flush()

    # --- Committee memberships ---
    db.add_all([
        CommitteeMembership(senator_id=s1.id, committee_id=finance.id, role="Chair"),
        CommitteeMembership(senator_id=s2.id, committee_id=finance.id, role="Member"),
        CommitteeMembership(senator_id=s2.id, committee_id=judiciary.id, role="Member"),
    ])
    db.commit()

    yield test_engine
    db.close()


# ---------------------------------------------------------------------------
# Test client with get_db override
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client(seeded_engine):
    """TestClient with get_db overridden to use the in-memory SQLite DB."""
    TestSession = sessionmaker(bind=seeded_engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.pop(get_db, None)
