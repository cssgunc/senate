"""Integration tests for admin carousel CRUD routes (ticket #71)."""

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
from app.models.CarouselSlide import CarouselSlide

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


def _seed(engine) -> list[int]:
    """Returns the IDs of the seeded slides in insertion order."""
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(Admin(email="admin@unc.edu", first_name="Admin", last_name="User", pid="100000001", role="admin"))
    db.flush()
    s1 = CarouselSlide(image_url="https://img.unc.edu/1.jpg", overlay_text="Slide 1", link_url=None, display_order=1, is_active=True)
    s2 = CarouselSlide(image_url="https://img.unc.edu/2.jpg", overlay_text="Slide 2", link_url=None, display_order=2, is_active=True)
    s3 = CarouselSlide(image_url="https://img.unc.edu/3.jpg", overlay_text="Slide 3", link_url=None, display_order=3, is_active=False)
    db.add_all([s1, s2, s3])
    db.commit()
    ids = [s1.id, s2.id, s3.id]
    db.close()
    return ids


def _clear():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture()
def write_engine():
    engine = _make_engine()
    _seed(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def write_engine_with_ids():
    engine = _make_engine()
    ids = _seed(engine)
    yield engine, ids
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


_CREATE_PAYLOAD = {
    "image_url": "https://img.unc.edu/new.jpg",
    "overlay_text": "New Slide",
    "link_url": "https://unc.edu",
    "display_order": 4,
    "is_active": True,
}


# ---------------------------------------------------------------------------
# POST /api/admin/carousel
# ---------------------------------------------------------------------------


class TestCreateAdminSlide:
    def test_returns_201(self, write_admin_client):
        assert write_admin_client.post("/api/admin/carousel", json=_CREATE_PAYLOAD).status_code == 201

    def test_response_shape(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/carousel", json=_CREATE_PAYLOAD).json()
        for key in ("id", "image_url", "display_order", "is_active"):
            assert key in resp

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "image_url"}
        assert write_admin_client.post("/api/admin/carousel", json=bad).status_code == 422

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.post("/api/admin/carousel", json=_CREATE_PAYLOAD).status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# PUT /api/admin/carousel/reorder
# ---------------------------------------------------------------------------


class TestReorderAdminSlides:
    def test_returns_200(self, write_engine_with_ids):
        engine, ids = write_engine_with_ids
        TestSession = sessionmaker(bind=engine)

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
        try:
            with TestClient(app) as c:
                resp = c.put("/api/admin/carousel/reorder", json={"slide_ids": ids})
                assert resp.status_code == 200
        finally:
            _clear()

    def test_reorder_changes_order(self, write_engine_with_ids):
        engine, ids = write_engine_with_ids
        TestSession = sessionmaker(bind=engine)
        reversed_ids = list(reversed(ids))

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
        try:
            with TestClient(app) as c:
                resp = c.put("/api/admin/carousel/reorder", json={"slide_ids": reversed_ids})
                assert resp.status_code == 200
                result_ids = [s["id"] for s in resp.json()]
                assert result_ids == reversed_ids
        finally:
            _clear()

    def test_partial_ids_returns_400(self, write_engine_with_ids):
        engine, ids = write_engine_with_ids
        TestSession = sessionmaker(bind=engine)

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
        try:
            with TestClient(app) as c:
                resp = c.put("/api/admin/carousel/reorder", json={"slide_ids": ids[:-1]})
                assert resp.status_code == 400
        finally:
            _clear()


# ---------------------------------------------------------------------------
# PUT /api/admin/carousel/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminSlide:
    def _create_slide(self, client) -> int:
        return client.post("/api/admin/carousel", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        slide_id = self._create_slide(write_admin_client)
        assert write_admin_client.put(f"/api/admin/carousel/{slide_id}", json={"is_active": False}).status_code == 200

    def test_fields_updated(self, write_admin_client):
        slide_id = self._create_slide(write_admin_client)
        resp = write_admin_client.put(f"/api/admin/carousel/{slide_id}", json={"overlay_text": "Changed"})
        assert resp.json()["overlay_text"] == "Changed"

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.put("/api/admin/carousel/999999", json={"is_active": False}).status_code == 404


# ---------------------------------------------------------------------------
# DELETE /api/admin/carousel/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminSlide:
    def _create_slide(self, client) -> int:
        return client.post("/api/admin/carousel", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        slide_id = self._create_slide(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/carousel/{slide_id}").status_code == 204

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/carousel/999999").status_code == 404

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/carousel/1").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
