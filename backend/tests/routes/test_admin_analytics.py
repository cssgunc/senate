"""Integration tests for GET /api/admin/analytics/summary (issue #206)."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin
from app.models.base import Base
from app.models.PageView import PageView
from app.utils.passwords import hash_password

_SQLITE_URL = "sqlite:///:memory:"


def _make_engine():
    engine = create_engine(_SQLITE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    original = {t: set(t.constraints) for t in Base.metadata.tables.values()}
    try:
        for t in Base.metadata.tables.values():
            t.constraints = {c for c in t.constraints if not isinstance(c, CheckConstraint)}
        Base.metadata.create_all(bind=engine)
    finally:
        for t, constraints in original.items():
            t.constraints = constraints
    return engine


def _seed(engine):
    now = datetime.now()
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(
        Admin(
            email="admin@unc.edu",
            first_name="Admin",
            last_name="User",
            onyen="user100000001",
            password_hash=hash_password("TestPassword123!"),
            role="admin",
        )
    )
    db.add_all(
        [
            PageView(
                path="/",
                referrer_host="google.com",
                user_agent="ua-1",
                visitor_hash="visitor-1",
                created_at=now - timedelta(hours=1),
            ),
            PageView(
                path="/",
                referrer_host="google.com",
                user_agent="ua-2",
                visitor_hash="visitor-2",
                created_at=now - timedelta(hours=2),
            ),
            PageView(
                path="/about",
                referrer_host=None,
                user_agent="ua-1",
                visitor_hash="visitor-1",
                created_at=now - timedelta(hours=3),
            ),
            # Outside the default 7-day window.
            PageView(
                path="/",
                referrer_host="google.com",
                user_agent="ua-3",
                visitor_hash="visitor-3",
                created_at=now - timedelta(days=30),
            ),
        ]
    )
    db.commit()
    db.close()


def _clear():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def analytics_engine():
    engine = _make_engine()
    _seed(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def admin_client(analytics_engine):
    TestSession = sessionmaker(bind=analytics_engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    def _override_current_user():
        db = TestSession()
        user = db.query(Admin).filter(Admin.email == "admin@unc.edu").first()
        db.close()
        return user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_current_user
    with TestClient(app) as c:
        yield c
    _clear()


class TestAnalyticsSummary:
    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/analytics/summary").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved

    def test_returns_200(self, admin_client):
        assert admin_client.get("/api/admin/analytics/summary").status_code == 200

    def test_default_range_excludes_old_rows(self, admin_client):
        data = admin_client.get("/api/admin/analytics/summary").json()
        assert data["range_days"] == 7
        assert data["total_pageviews"] == 3

    def test_unique_visitors_counted_by_distinct_hash(self, admin_client):
        data = admin_client.get("/api/admin/analytics/summary").json()
        assert data["unique_visitors"] == 2

    def test_wider_range_includes_old_row(self, admin_client):
        data = admin_client.get("/api/admin/analytics/summary?days=90").json()
        assert data["total_pageviews"] == 4

    def test_top_paths_sorted_by_count(self, admin_client):
        data = admin_client.get("/api/admin/analytics/summary").json()
        assert data["top_paths"][0] == {"path": "/", "count": 2}

    def test_top_referrers_excludes_null(self, admin_client):
        data = admin_client.get("/api/admin/analytics/summary").json()
        hosts = {row["referrer_host"] for row in data["top_referrers"]}
        assert None not in hosts
        assert "google.com" in hosts

    def test_days_out_of_range_returns_422(self, admin_client):
        assert admin_client.get("/api/admin/analytics/summary?days=0").status_code == 422
        assert admin_client.get("/api/admin/analytics/summary?days=91").status_code == 422
