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


def _seed_navigation_flow(engine):
    """Seed pageviews specifically shaped to exercise session reconstruction.

    visitor-a: "/" -> "/about" (5 min apart, same session), then a 45-minute
    gap, then "/legislation" (new session) -- 2 Start edges + 1 page edge.
    visitor-b: single pageview on "/" -- 1 Start edge, no page edge.
    visitor-c: "/" -> "/" (2 min apart, same path) -- 1 Start edge, self-loop dropped.
    """
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
                visitor_hash="visitor-a",
                created_at=now - timedelta(hours=2),
            ),
            PageView(
                path="/about",
                visitor_hash="visitor-a",
                created_at=now - timedelta(hours=2) + timedelta(minutes=5),
            ),
            PageView(
                path="/legislation",
                visitor_hash="visitor-a",
                created_at=now - timedelta(hours=2) + timedelta(minutes=50),
            ),
            PageView(
                path="/",
                visitor_hash="visitor-b",
                created_at=now - timedelta(hours=1),
            ),
            PageView(
                path="/",
                visitor_hash="visitor-c",
                created_at=now - timedelta(minutes=30),
            ),
            PageView(
                path="/",
                visitor_hash="visitor-c",
                created_at=now - timedelta(minutes=28),
            ),
        ]
    )
    db.commit()
    db.close()


@pytest.fixture()
def nav_flow_engine():
    engine = _make_engine()
    _seed_navigation_flow(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def nav_flow_client(nav_flow_engine):
    TestSession = sessionmaker(bind=nav_flow_engine)

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


class TestNavigationFlow:
    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/analytics/navigation-flow").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved

    def test_returns_200(self, nav_flow_client):
        assert nav_flow_client.get("/api/admin/analytics/navigation-flow").status_code == 200

    def test_gap_over_threshold_splits_session(self, nav_flow_client):
        data = nav_flow_client.get("/api/admin/analytics/navigation-flow").json()
        links = {(link["source"], link["target"]): link["count"] for link in data["links"]}
        # visitor-a's first session, visitor-b, and visitor-c's first view all land here.
        assert links[("__start__", "/")] == 3
        assert links[("/", "/about")] == 1
        assert links[("__start__", "/legislation")] == 1  # visitor-a's second session (gap > 30 min)

    def test_self_loop_excluded(self, nav_flow_client):
        data = nav_flow_client.get("/api/admin/analytics/navigation-flow").json()
        links = {(link["source"], link["target"]) for link in data["links"]}
        assert ("/", "/") not in links

    def test_single_pageview_visitor_contributes_only_start_edge(self, nav_flow_client):
        data = nav_flow_client.get("/api/admin/analytics/navigation-flow").json()
        links = {(link["source"], link["target"]): link["count"] for link in data["links"]}
        # visitor-b's only view and visitor-c's first view both land here; visitor-c
        # contributes no page-to-page edge since its second view is a same-path self-loop.
        assert links[("__start__", "/")] == 3

    def test_total_sessions_counts_all_start_edges(self, nav_flow_client):
        data = nav_flow_client.get("/api/admin/analytics/navigation-flow").json()
        # visitor-a: 2 sessions, visitor-b: 1 session, visitor-c: 1 session
        assert data["total_sessions"] == 4

    def test_days_out_of_range_returns_422(self, nav_flow_client):
        assert nav_flow_client.get("/api/admin/analytics/navigation-flow?days=0").status_code == 422
        assert nav_flow_client.get("/api/admin/analytics/navigation-flow?days=91").status_code == 422
