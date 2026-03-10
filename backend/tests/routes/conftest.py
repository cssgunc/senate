"""Fixtures for route integration tests.

Uses an in-memory SQLite database so tests run without a SQL Server connection.
All GET-only endpoints are tested against seeded fixture data.
"""

from datetime import date, datetime, time

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
from app.models.BudgetData import BudgetData
from app.models.CalendarEvent import CalendarEvent
from app.models.CarouselSlide import CarouselSlide
from app.models.cms import Committee, CommitteeMembership, News, Staff, StaticPageContent
from app.models.District import District, DistrictMapping
from app.models.FinanceHearingConfig import FinanceHearingConfig
from app.models.FinanceHearingDate import FinanceHearingDate

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
        table.constraints = {c for c in table.constraints if not isinstance(c, CheckConstraint)}

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
    db.add_all(
        [
            CommitteeMembership(senator_id=s1.id, committee_id=finance.id, role="Chair"),
            CommitteeMembership(senator_id=s2.id, committee_id=finance.id, role="Member"),
            CommitteeMembership(senator_id=s2.id, committee_id=judiciary.id, role="Member"),
        ]
    )
    db.flush()

    # --- Calendar events ---
    db.add_all([
        CalendarEvent(
            title="General Body Meeting",
            description="Monthly meeting",
            start_datetime=datetime(2026, 4, 1, 18, 0),
            end_datetime=datetime(2026, 4, 1, 19, 30),
            location="The Pit",
            event_type="meeting",
            is_published=True,
            created_by=admin.id,
        ),
        CalendarEvent(
            title="Finance Hearing",
            description=None,
            start_datetime=datetime(2026, 4, 15, 9, 0),
            end_datetime=datetime(2026, 4, 15, 11, 0),
            location="Union",
            event_type="hearing",
            is_published=True,
            created_by=admin.id,
        ),
        CalendarEvent(
            title="Draft Event",
            description="Not published",
            start_datetime=datetime(2026, 5, 1, 10, 0),
            end_datetime=datetime(2026, 5, 1, 11, 0),
            location=None,
            event_type="meeting",
            is_published=False,
            created_by=admin.id,
        ),
    ])
    db.flush()

    # --- Carousel slides ---
    slide1 = CarouselSlide(
        image_url="https://img.unc.edu/slide1.jpg",
        overlay_text="Welcome to Senate",
        link_url="https://unc.edu",
        display_order=1,
        is_active=True,
    )
    slide2 = CarouselSlide(
        image_url="https://img.unc.edu/slide2.jpg",
        overlay_text=None,
        link_url=None,
        display_order=2,
        is_active=True,
    )
    slide3_inactive = CarouselSlide(
        image_url="https://img.unc.edu/slide3.jpg",
        overlay_text="Hidden",
        link_url=None,
        display_order=3,
        is_active=False,
    )
    db.add_all([slide1, slide2, slide3_inactive])
    db.flush()

    # --- District mappings ---
    db.add_all(
        [
            DistrictMapping(district_id=d1.id, mapping_value="on-campus"),
            DistrictMapping(district_id=d2.id, mapping_value="off-campus"),
        ]
    )
    db.flush()

    # --- Staff ---
    staff1 = Staff(
        first_name="First",
        last_name="Staff",
        title="Director",
        email="first@unc.edu",
        display_order=1,
        is_active=True,
    )
    staff2 = Staff(
        first_name="Second",
        last_name="Staff",
        title="Manager",
        email="second@unc.edu",
        display_order=2,
        is_active=True,
    )
    staff3_inactive = Staff(
        first_name="Inactive",
        last_name="Person",
        title="Assistant",
        email="inactive@unc.edu",
        display_order=3,
        is_active=False,
    )
    db.add_all([staff1, staff2, staff3_inactive])
    db.flush()

    # --- Finance hearing config and dates ---
    fhc = FinanceHearingConfig(
        is_active=True,
        season_start=date(2026, 1, 15),
        season_end=date(2026, 5, 15),
        updated_by=admin.id,
    )
    db.add(fhc)
    db.flush()
    db.add_all(
        [
            FinanceHearingDate(
                hearing_date=date(2026, 2, 1),
                hearing_time=time(9, 0),
                location="The Pit",
                description="Morning slot",
                is_full=False,
            ),
            FinanceHearingDate(
                hearing_date=date(2026, 2, 2),
                hearing_time=time(14, 0),
                location="Union",
                description=None,
                is_full=True,
            ),
        ]
    )
    db.flush()

    # --- Budget data (FY2026 = most recent; FY2025 = older) ---
    parent_budget = BudgetData(
        fiscal_year="FY2026",
        category="Operations",
        amount=100000.00,
        description="Operating budget",
        parent_category_id=None,
        display_order=1,
        updated_by=admin.id,
    )
    db.add(parent_budget)
    db.flush()
    db.add_all(
        [
            BudgetData(
                fiscal_year="FY2026",
                category="Salaries",
                amount=60000.00,
                description=None,
                parent_category_id=parent_budget.id,
                display_order=2,
                updated_by=admin.id,
            ),
            BudgetData(
                fiscal_year="FY2026",
                category="Supplies",
                amount=40000.00,
                description=None,
                parent_category_id=parent_budget.id,
                display_order=3,
                updated_by=admin.id,
            ),
            BudgetData(
                fiscal_year="FY2025",
                category="Old Operations",
                amount=90000.00,
                description=None,
                parent_category_id=None,
                display_order=1,
                updated_by=admin.id,
            ),
        ]
    )
    db.flush()

    # --- Static page content ---
    db.add(
        StaticPageContent(
            page_slug="powers-of-senate",
            title="Powers of the Senate",
            body="The senate has the power to...",
            last_edited_by=admin.id,
        )
    )
    db.flush()

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


@pytest.fixture(scope="function")
def db_session(seeded_engine):
    """Direct DB session for targeted edge-case test setup."""
    TestSession = sessionmaker(bind=seeded_engine)
    db = TestSession()
    try:
        yield db
        db.commit()
    finally:
        db.close()
