"""Integration tests for admin news CRUD routes (ticket #62).

Auth is not yet implemented (#61), so get_current_user is overridden in each
fixture to inject a pre-seeded Admin row directly.  require_role("admin")
internally calls Depends(get_current_user), so overriding get_current_user is
sufficient to exercise 403 behaviour for staff users on DELETE.

Read tests (GET) use a module-scoped engine for speed.
Write tests (POST/PUT/DELETE) each get a fresh function-scoped engine so that
mutations do not bleed across tests.
"""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — registers all models with Base.metadata
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin
from app.models.base import Base
from app.models.cms import News

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SQLITE_URL = "sqlite:///:memory:"


def _make_engine():
    engine = create_engine(
        _SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Strip SQL Server-specific CHECK constraints only for table creation,
    # then restore metadata so other test modules are unaffected.
    original_constraints = {
        table: set(table.constraints) for table in Base.metadata.tables.values()
    }
    try:
        for table in Base.metadata.tables.values():
            table.constraints = {c for c in table.constraints if not isinstance(c, CheckConstraint)}
        Base.metadata.create_all(bind=engine)
    finally:
        for table, constraints in original_constraints.items():
            table.constraints = constraints

    return engine


def _seed(engine) -> tuple[Admin, Admin]:
    """Insert one admin, one staff, and two news articles (1 published, 1 draft).

    Returns (admin_user, staff_user).
    """
    Session = sessionmaker(bind=engine)
    db = Session()

    admin_user = Admin(
        email="admin@unc.edu",
        first_name="Admin",
        last_name="User",
        pid="100000001",
        role="admin",
    )
    staff_user = Admin(
        email="staff@unc.edu",
        first_name="Staff",
        last_name="User",
        pid="200000002",
        role="staff",
    )
    db.add_all([admin_user, staff_user])
    db.flush()

    db.add_all(
        [
            News(
                title="Published Article",
                body="Published body.",
                summary="Published summary.",
                image_url=None,
                author_id=admin_user.id,
                date_published=datetime(2026, 3, 1, 10, 0),
                date_last_edited=datetime(2026, 3, 1, 10, 0),
                is_published=True,
            ),
            News(
                title="Draft Article",
                body="Draft body.",
                summary="Draft summary.",
                image_url=None,
                author_id=admin_user.id,
                date_published=datetime(2026, 2, 1, 10, 0),
                date_last_edited=datetime(2026, 2, 1, 10, 0),
                is_published=False,
            ),
        ]
    )
    db.commit()
    db.close()
    return admin_user, staff_user


def _make_client(engine, current_user: Admin) -> TestClient:
    """Build a TestClient that overrides get_db and get_current_user."""
    TestSession = sessionmaker(bind=engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    def _override_get_current_user():
        # Re-query so the object is bound to a session
        db = TestSession()
        user = db.query(Admin).filter(Admin.id == current_user.id).first()
        db.close()
        return user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user
    return TestClient(app)


def _clear_overrides():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# Module-scoped fixtures (read tests)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def read_engine():
    engine = _make_engine()
    _seed(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def admin_user_id(read_engine):
    db = sessionmaker(bind=read_engine)()
    user = db.query(Admin).filter(Admin.email == "admin@unc.edu").first()
    db.close()
    return user.id


@pytest.fixture(scope="module")
def staff_user_id(read_engine):
    db = sessionmaker(bind=read_engine)()
    user = db.query(Admin).filter(Admin.email == "staff@unc.edu").first()
    db.close()
    return user.id


@pytest.fixture(scope="module")
def admin_read_client(read_engine, admin_user_id):
    TestSession = sessionmaker(bind=read_engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    def _override_current_user():
        db = TestSession()
        user = db.query(Admin).filter(Admin.id == admin_user_id).first()
        db.close()
        return user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_current_user
    with TestClient(app) as c:
        yield c
    _clear_overrides()


# ---------------------------------------------------------------------------
# Function-scoped fixtures (write tests)
# ---------------------------------------------------------------------------


@pytest.fixture()
def write_engine():
    engine = _make_engine()
    _seed(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def write_admin_client(write_engine):
    TestSession = sessionmaker(bind=write_engine)

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
    _clear_overrides()


@pytest.fixture()
def write_staff_client(write_engine):
    TestSession = sessionmaker(bind=write_engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    def _override_current_user():
        db = TestSession()
        user = db.query(Admin).filter(Admin.email == "staff@unc.edu").first()
        db.close()
        return user

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_current_user
    with TestClient(app) as c:
        yield c
    _clear_overrides()


# ---------------------------------------------------------------------------
# GET /api/admin/news
# ---------------------------------------------------------------------------


class TestListAdminNews:
    def test_returns_200(self, admin_read_client):
        assert admin_read_client.get("/api/admin/news").status_code == 200

    def test_pagination_shape(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news").json()
        for key in ("items", "total", "page", "limit"):
            assert key in data

    def test_includes_drafts(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news").json()
        titles = [i["title"] for i in data["items"]]
        assert "Draft Article" in titles

    def test_total_includes_all_articles(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news").json()
        assert data["total"] == 2

    def test_is_published_field_present(self, admin_read_client):
        item = admin_read_client.get("/api/admin/news").json()["items"][0]
        assert "is_published" in item

    def test_filter_published_only(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news?is_published=true").json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Published Article"

    def test_filter_drafts_only(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news?is_published=false").json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Draft Article"

    def test_default_page_and_limit(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news").json()
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_custom_limit(self, admin_read_client):
        data = admin_read_client.get("/api/admin/news?limit=1").json()
        assert len(data["items"]) == 1
        assert data["total"] == 2

    def test_invalid_page_returns_422(self, admin_read_client):
        assert admin_read_client.get("/api/admin/news?page=0").status_code == 422

    def test_unauthenticated_is_rejected(self):
        """Without auth override, unauthenticated requests must be rejected.

        While #61 is pending, the stub returns 501. Once auth is implemented,
        this should naturally become 401/403.
        """
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/news").status_code in {401, 403, 501}
        finally:
            if saved is not None:
                app.dependency_overrides[get_current_user] = saved

    def test_unauthenticated_create_is_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        payload = {
            "title": "New Article",
            "body": "Body content.",
            "summary": "A summary.",
            "image_url": None,
            "is_published": False,
        }
        try:
            with TestClient(app) as c:
                assert c.post("/api/admin/news", json=payload).status_code in {401, 403, 501}
        finally:
            if saved is not None:
                app.dependency_overrides[get_current_user] = saved

    def test_unauthenticated_update_is_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        payload = {
            "title": "Updated Title",
            "body": "Updated body.",
            "summary": "Updated summary.",
            "image_url": None,
            "is_published": True,
        }
        try:
            with TestClient(app) as c:
                assert c.put("/api/admin/news/1", json=payload).status_code in {401, 403, 501}
        finally:
            if saved is not None:
                app.dependency_overrides[get_current_user] = saved

    def test_unauthenticated_delete_is_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/news/1").status_code in {401, 403, 501}
        finally:
            if saved is not None:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# POST /api/admin/news
# ---------------------------------------------------------------------------


class TestCreateNews:
    _payload = {
        "title": "New Article",
        "body": "Body content.",
        "summary": "A summary.",
        "image_url": None,
        "is_published": False,
    }

    def test_returns_201(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/news", json=self._payload)
        assert resp.status_code == 201

    def test_response_contains_id(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/news", json=self._payload)
        assert "id" in resp.json()

    def test_author_id_set_from_current_user(self, write_admin_client, write_engine):
        resp = write_admin_client.post("/api/admin/news", json=self._payload)
        article_id = resp.json()["id"]
        db = sessionmaker(bind=write_engine)()
        article = db.query(News).filter(News.id == article_id).first()
        admin = db.query(Admin).filter(Admin.email == "admin@unc.edu").first()
        db.close()
        assert article.author_id == admin.id

    def test_is_published_field_honoured(self, write_admin_client):
        payload = {**self._payload, "is_published": True}
        resp = write_admin_client.post("/api/admin/news", json=payload)
        assert resp.json()["is_published"] is True

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {k: v for k, v in self._payload.items() if k != "title"}
        assert write_admin_client.post("/api/admin/news", json=bad).status_code == 422

    def test_article_appears_in_list_after_creation(self, write_admin_client):
        write_admin_client.post("/api/admin/news", json=self._payload)
        data = write_admin_client.get("/api/admin/news").json()
        titles = [i["title"] for i in data["items"]]
        assert "New Article" in titles


# ---------------------------------------------------------------------------
# PUT /api/admin/news/{id}
# ---------------------------------------------------------------------------


class TestUpdateNews:
    def _get_any_id(self, client) -> int:
        return client.get("/api/admin/news").json()["items"][0]["id"]

    def test_returns_200(self, write_admin_client):
        news_id = self._get_any_id(write_admin_client)
        payload = {
            "title": "Updated Title",
            "body": "Updated body.",
            "summary": "Updated summary.",
            "image_url": None,
            "is_published": True,
        }
        assert write_admin_client.put(f"/api/admin/news/{news_id}", json=payload).status_code == 200

    def test_fields_updated(self, write_admin_client):
        news_id = self._get_any_id(write_admin_client)
        payload = {
            "title": "Changed Title",
            "body": "Changed body.",
            "summary": "Changed summary.",
            "image_url": "https://img.unc.edu/new.jpg",
            "is_published": True,
        }
        resp = write_admin_client.put(f"/api/admin/news/{news_id}", json=payload)
        data = resp.json()
        assert data["title"] == "Changed Title"
        assert data["image_url"] == "https://img.unc.edu/new.jpg"
        assert data["is_published"] is True

    def test_returns_404_for_missing_article(self, write_admin_client):
        payload = {
            "title": "X",
            "body": "X",
            "summary": "X",
            "image_url": None,
            "is_published": False,
        }
        assert write_admin_client.put("/api/admin/news/999999", json=payload).status_code == 404

    def test_staff_can_update(self, write_staff_client):
        news_id = write_staff_client.get("/api/admin/news").json()["items"][0]["id"]
        payload = {
            "title": "Staff Update",
            "body": "Staff body.",
            "summary": "Staff summary.",
            "image_url": None,
            "is_published": False,
        }
        assert write_staff_client.put(f"/api/admin/news/{news_id}", json=payload).status_code == 200


# ---------------------------------------------------------------------------
# DELETE /api/admin/news/{id}
# ---------------------------------------------------------------------------


class TestDeleteNews:
    def _get_any_id(self, client) -> int:
        return client.get("/api/admin/news").json()["items"][0]["id"]

    def test_returns_204(self, write_admin_client):
        news_id = self._get_any_id(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/news/{news_id}").status_code == 204

    def test_article_gone_after_delete(self, write_admin_client):
        news_id = self._get_any_id(write_admin_client)
        write_admin_client.delete(f"/api/admin/news/{news_id}")
        assert write_admin_client.get("/api/admin/news").json()["total"] == 1

    def test_returns_404_for_missing_article(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/news/999999").status_code == 404

    def test_staff_cannot_delete(self, write_staff_client):
        news_id = self._get_any_id(write_staff_client)
        assert write_staff_client.delete(f"/api/admin/news/{news_id}").status_code == 403
