"""Integration tests for admin static pages routes (ticket #71)."""

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
from app.models.cms import StaticPageContent

_SQLITE_URL = "sqlite:///:memory:"


def _make_engine():
    engine = create_engine(
        _SQLITE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

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
    Session = sessionmaker(bind=engine)
    db = Session()
    admin_user = Admin(
        email="admin@unc.edu", first_name="Admin", last_name="User", pid="100000001", role="admin"
    )
    db.add(admin_user)
    db.flush()
    db.add_all(
        [
            StaticPageContent(
                page_slug="powers-of-senate",
                title="Powers of the Senate",
                body="The senate has...",
                last_edited_by=admin_user.id,
            ),
            StaticPageContent(
                page_slug="how-a-bill-becomes-law",
                title="How a Bill Becomes Law",
                body="A bill starts as...",
                last_edited_by=admin_user.id,
            ),
        ]
    )
    db.commit()
    db.close()


def _clear():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="module")
def read_engine():
    engine = _make_engine()
    _seed(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def admin_read_client(read_engine):
    TestSession = sessionmaker(bind=read_engine)

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
    _clear()


# ---------------------------------------------------------------------------
# GET /api/admin/pages
# ---------------------------------------------------------------------------


class TestListAdminPages:
    def test_returns_200(self, admin_read_client):
        assert admin_read_client.get("/api/admin/pages").status_code == 200

    def test_returns_list_of_pages(self, admin_read_client):
        data = admin_read_client.get("/api/admin/pages").json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_response_shape(self, admin_read_client):
        item = admin_read_client.get("/api/admin/pages").json()[0]
        for key in ("id", "page_slug", "title", "body", "updated_at"):
            assert key in item

    def test_slugs_present(self, admin_read_client):
        slugs = {p["page_slug"] for p in admin_read_client.get("/api/admin/pages").json()}
        assert "powers-of-senate" in slugs
        assert "how-a-bill-becomes-law" in slugs

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/pages").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# PUT /api/admin/pages/{slug}
# ---------------------------------------------------------------------------


class TestUpdateAdminPage:
    _payload = {"title": "Updated Title", "body": "Updated body content."}

    def test_returns_200(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/pages/powers-of-senate", json=self._payload
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        resp = write_admin_client.put("/api/admin/pages/powers-of-senate", json=self._payload)
        assert resp.json()["title"] == "Updated Title"
        assert resp.json()["body"] == "Updated body content."

    def test_slug_unchanged(self, write_admin_client):
        resp = write_admin_client.put("/api/admin/pages/powers-of-senate", json=self._payload)
        assert resp.json()["page_slug"] == "powers-of-senate"

    def test_returns_404_for_unknown_slug(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/pages/nonexistent-page", json=self._payload
            ).status_code
            == 404
        )

    def test_missing_required_field_returns_422(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/pages/powers-of-senate", json={"title": "Only Title"}
            ).status_code
            == 422
        )

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.put(
                    "/api/admin/pages/powers-of-senate", json=self._payload
                ).status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
