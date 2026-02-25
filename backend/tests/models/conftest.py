"""Fixtures for model tests.

Uses an in-memory SQLite database so tests run without a SQL Server connection.
"""

import pytest
from sqlalchemy import CheckConstraint, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import all models so they are registered with Base before create_all
import app.models  # noqa: F401
from app.models import Admin, Senator
from app.models.base import Base
from app.models.cms import Committee
from app.models.District import District

# ---------------------------------------------------------------------------
# Shared in-memory SQLite engine (session-scoped — created once per test run)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def engine():
    """In-memory SQLite engine shared across all model tests in this directory."""
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # SQLite does not enforce FK constraints by default — enable them
    @event.listens_for(_engine, "connect")
    def enforce_foreign_keys(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Remove SQL Server-specific CHECK constraints before creating tables on SQLite
    for table in Base.metadata.tables.values():
        table.constraints = {
            c for c in table.constraints if not isinstance(c, CheckConstraint)
        }

    Base.metadata.create_all(bind=_engine)
    yield _engine
    Base.metadata.drop_all(bind=_engine)


# ---------------------------------------------------------------------------
# Per-test transactional session — rolls back after every test for isolation
# ---------------------------------------------------------------------------


@pytest.fixture()
def session(engine):
    """Transactional session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    _Session = sessionmaker(bind=connection, autoflush=False)
    db = _Session()

    yield db

    db.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Reusable FK-target instances
# ---------------------------------------------------------------------------


@pytest.fixture()
def district(session):
    """A flushed District instance available as a FK target in tests."""
    d = District(district_name="District 1", description="Test district")
    session.add(d)
    session.flush()
    return d


@pytest.fixture()
def admin(session):
    """A flushed Admin instance available as a FK target in tests."""
    a = Admin(
        email="test.admin@unc.edu",
        first_name="Test",
        last_name="Admin",
        pid="123456789",
        role="admin",
    )
    session.add(a)
    session.flush()
    return a


@pytest.fixture()
def senator(session, district):
    """A flushed Senator instance available as a FK target in tests."""
    s = Senator(
        first_name="Jane",
        last_name="Doe",
        email="jane.doe@unc.edu",
        district=district.id,
        session_number=1,
    )
    session.add(s)
    session.flush()
    return s


@pytest.fixture()
def committee(session):
    """A flushed Committee instance for CommitteeMembership tests."""
    c = Committee(
        name="Finance Committee",
        description="Oversees the senate budget.",
        chair_name="John Chair",
        chair_email="chair@unc.edu",
        is_active=True,
    )
    session.add(c)
    session.flush()
    return c
