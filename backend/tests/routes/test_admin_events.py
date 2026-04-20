"""Integration tests for admin calendar event CRUD routes (ticket #71)."""

from datetime import datetime

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
from app.models.CalendarEvent import CalendarEvent

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
    admin_user = Admin(email="admin@unc.edu", first_name="Admin", last_name="User", pid="100000001", role="admin")
    staff_user = Admin(email="staff@unc.edu", first_name="Staff", last_name="User", pid="200000002", role="staff")
    db.add_all([admin_user, staff_user])
    db.flush()
    db.add(CalendarEvent(
        title="Existing Event",
        start_datetime=datetime(2026, 4, 1, 18, 0),
        end_datetime=datetime(2026, 4, 1, 19, 0),
        event_type="meeting",
        is_published=True,
        created_by=admin_user.id,
        description=None,
        location=None,
    ))
    db.commit()
    db.close()


def _clear():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


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
    _clear()


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
    _clear()


# ---------------------------------------------------------------------------
# POST /api/admin/events
# ---------------------------------------------------------------------------

_CREATE_PAYLOAD = {
    "title": "New Event",
    "description": "A test event",
    "start_datetime": "2026-06-01T10:00:00",
    "end_datetime": "2026-06-01T11:00:00",
    "location": "Chapel Hill",
    "event_type": "meeting",
    "is_published": False,
}


class TestCreateAdminEvent:
    def test_returns_201(self, write_admin_client):
        assert write_admin_client.post("/api/admin/events", json=_CREATE_PAYLOAD).status_code == 201

    def test_response_contains_id_and_is_published(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/events", json=_CREATE_PAYLOAD).json()
        assert "id" in resp
        assert "is_published" in resp

    def test_is_published_true(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/events", json={**_CREATE_PAYLOAD, "is_published": True})
        assert resp.json()["is_published"] is True

    def test_end_before_start_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "end_datetime": "2026-06-01T09:00:00"}
        assert write_admin_client.post("/api/admin/events", json=bad).status_code == 422

    def test_missing_title_returns_422(self, write_admin_client):
        bad = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "title"}
        assert write_admin_client.post("/api/admin/events", json=bad).status_code == 422

    def test_staff_can_create(self, write_staff_client):
        assert write_staff_client.post("/api/admin/events", json=_CREATE_PAYLOAD).status_code == 201

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.post("/api/admin/events", json=_CREATE_PAYLOAD).status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# PUT /api/admin/events/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminEvent:
    def _create_event(self, client) -> int:
        return client.post("/api/admin/events", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        event_id = self._create_event(write_admin_client)
        assert write_admin_client.put(f"/api/admin/events/{event_id}", json={"title": "Updated"}).status_code == 200

    def test_fields_updated(self, write_admin_client):
        event_id = self._create_event(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/events/{event_id}",
            json={"title": "Changed", "is_published": True},
        )
        assert resp.json()["title"] == "Changed"
        assert resp.json()["is_published"] is True

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.put("/api/admin/events/999999", json={"title": "X"}).status_code == 404

    def test_staff_can_update(self, write_staff_client):
        event_id = self._create_event(write_staff_client)
        assert write_staff_client.put(f"/api/admin/events/{event_id}", json={"title": "Staff"}).status_code == 200

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.put("/api/admin/events/1", json={"title": "X"}).status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# DELETE /api/admin/events/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminEvent:
    def _create_event(self, client) -> int:
        return client.post("/api/admin/events", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        event_id = self._create_event(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/events/{event_id}").status_code == 204

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/events/999999").status_code == 404

    def test_staff_cannot_delete(self, write_staff_client):
        event_id = self._create_event(write_staff_client)
        assert write_staff_client.delete(f"/api/admin/events/{event_id}").status_code == 403

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/events/1").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
