"""Integration tests for admin staff CRUD routes (ticket #71)."""

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
from app.models.cms import Staff

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
    db.add_all(
        [
            Admin(
                email="admin@unc.edu",
                first_name="Admin",
                last_name="User",
                pid="100000001",
                role="admin",
            ),
            Admin(
                email="staff@unc.edu",
                first_name="Staff",
                last_name="User",
                pid="200000002",
                role="staff",
            ),
        ]
    )
    db.flush()
    db.add(
        Staff(
            first_name="Existing",
            last_name="Person",
            title="Director",
            email="existing@unc.edu",
            display_order=1,
        )
    )
    db.commit()
    db.close()


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
    "first_name": "New",
    "last_name": "Staffer",
    "title": "Coordinator",
    "email": "newstaffer@unc.edu",
    "display_order": 5,
}


# ---------------------------------------------------------------------------
# POST /api/admin/staff
# ---------------------------------------------------------------------------


class TestCreateAdminStaff:
    def test_returns_201(self, write_admin_client):
        assert write_admin_client.post("/api/admin/staff", json=_CREATE_PAYLOAD).status_code == 201

    def test_response_shape(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/staff", json=_CREATE_PAYLOAD).json()
        for key in ("id", "first_name", "last_name", "title", "email"):
            assert key in resp

    def test_photo_url_can_be_set_on_create(self, write_admin_client):
        payload = {**_CREATE_PAYLOAD, "photo_url": "/api/uploads/staff-photo.jpg"}
        resp = write_admin_client.post("/api/admin/staff", json=payload)
        assert resp.status_code == 201
        assert resp.json()["photo_url"] == "/api/uploads/staff-photo.jpg"

    def test_photo_url_defaults_to_none_on_create(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/staff", json=_CREATE_PAYLOAD)
        assert resp.status_code == 201
        assert resp.json()["photo_url"] is None

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "email"}
        assert write_admin_client.post("/api/admin/staff", json=bad).status_code == 422

    def test_invalid_email_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "email": "not-an-email"}
        assert write_admin_client.post("/api/admin/staff", json=bad).status_code == 422

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.post("/api/admin/staff", json=_CREATE_PAYLOAD).status_code in {
                    401,
                    403,
                    501,
                }
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# PUT /api/admin/staff/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminStaff:
    def _create_staff(self, client) -> int:
        return client.post("/api/admin/staff", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        staff_id = self._create_staff(write_admin_client)
        assert (
            write_admin_client.put(
                f"/api/admin/staff/{staff_id}", json={"title": "Updated"}
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        staff_id = self._create_staff(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/staff/{staff_id}", json={"title": "Manager", "is_active": False}
        )
        assert resp.json()["title"] == "Manager"

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.put("/api/admin/staff/999999", json={"title": "X"}).status_code
            == 404
        )

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.put("/api/admin/staff/1", json={"title": "X"}).status_code in {
                    401,
                    403,
                    501,
                }
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# DELETE /api/admin/staff/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminStaff:
    def _create_staff(self, client) -> int:
        return client.post("/api/admin/staff", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        staff_id = self._create_staff(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/staff/{staff_id}").status_code == 204

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/staff/999999").status_code == 404

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/staff/1").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
