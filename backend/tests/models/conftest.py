"""Fixtures for CMS model tests.

Uses an in-memory SQLite database so tests run without a SQL Server connection.
Stub Admin and Senator models satisfy the FK constraints referenced in cms.py.
These stubs will be replaced by real models once issue #3 is merged.
"""

import pytest
from sqlalchemy import Integer, String, create_engine, event
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base

# ---------------------------------------------------------------------------
# Stub models — FK targets defined in cms.py that come from issue #3.
# Must be registered with Base BEFORE cms.py models are imported so that
# SQLAlchemy's mapper can resolve the relationship strings.
# ---------------------------------------------------------------------------


class Admin(Base):
    """Minimal Admin stub to satisfy FKs: author_id, last_edited_by, updated_by."""

    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # back_populates counterparts required by cms.py relationship declarations
    news_articles = relationship(
        "News", back_populates="author", foreign_keys="[News.author_id]"
    )
    edited_pages = relationship(
        "StaticPageContent",
        back_populates="editor",
        foreign_keys="[StaticPageContent.last_edited_by]",
    )
    config_updates = relationship(
        "AppConfig", back_populates="updater", foreign_keys="[AppConfig.updated_by]"
    )


class Senator(Base):
    """Minimal Senator stub to satisfy FKs: senator_id, chair_senator_id."""

    __tablename__ = "senator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # back_populates counterpart required by CommitteeMembership.senator
    committee_memberships = relationship(
        "CommitteeMembership",
        back_populates="senator",
        foreign_keys="[CommitteeMembership.senator_id]",
    )


# Import Committee after stubs are registered so the relationship string resolves.
# All other CMS models are imported directly in test_cms_models.py where they are used.
from app.models.cms import Committee  # noqa: E402

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
def admin(session):
    """A flushed Admin instance available as a FK target in tests."""
    a = Admin(email="test.admin@unc.edu", first_name="Test", last_name="Admin")
    session.add(a)
    session.flush()
    return a


@pytest.fixture()
def senator(session):
    """A flushed Senator instance available as a FK target in tests."""
    s = Senator(first_name="Jane", last_name="Doe")
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
