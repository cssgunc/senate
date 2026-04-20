"""Integration tests for admin finance hearing CRUD routes (ticket #71)."""

from datetime import date, time

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
from app.models.FinanceHearingConfig import FinanceHearingConfig
from app.models.FinanceHearingDate import FinanceHearingDate

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
    config = FinanceHearingConfig(
        is_active=True,
        season_start=date(2026, 1, 1),
        season_end=date(2026, 5, 31),
        updated_by=admin_user.id,
    )
    db.add(config)
    db.flush()
    db.add(
        FinanceHearingDate(
            hearing_date=date(2026, 2, 10),
            hearing_time=time(9, 0),
            location="The Pit",
            description="Morning slot",
            is_full=False,
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


# ---------------------------------------------------------------------------
# PUT /api/admin/finance-hearings/config
# ---------------------------------------------------------------------------


class TestUpdateFinanceConfig:
    _payload = {"is_active": False, "season_start": "2026-03-01", "season_end": "2026-06-30"}

    def test_returns_200(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/finance-hearings/config", json=self._payload
            ).status_code
            == 200
        )

    def test_config_updated(self, write_admin_client):
        resp = write_admin_client.put("/api/admin/finance-hearings/config", json=self._payload)
        assert resp.json()["is_active"] is False
        assert resp.json()["season_start"] == "2026-03-01"

    def test_inactive_config_returns_empty_dates(self, write_admin_client):
        resp = write_admin_client.put(
            "/api/admin/finance-hearings/config", json={**self._payload, "is_active": False}
        )
        assert resp.json()["dates"] == []

    def test_active_config_returns_dates(self, write_admin_client):
        resp = write_admin_client.put(
            "/api/admin/finance-hearings/config", json={**self._payload, "is_active": True}
        )
        assert isinstance(resp.json()["dates"], list)

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {"season_start": "2026-03-01", "season_end": "2026-06-30"}
        assert (
            write_admin_client.put("/api/admin/finance-hearings/config", json=bad).status_code
            == 422
        )

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.put(
                    "/api/admin/finance-hearings/config", json=self._payload
                ).status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# POST /api/admin/finance-hearings/dates
# ---------------------------------------------------------------------------

_DATE_PAYLOAD = {
    "hearing_date": "2026-03-15",
    "hearing_time": "10:00:00",
    "location": "Union",
    "description": "Afternoon slot",
}


class TestCreateFinanceDate:
    def test_returns_201(self, write_admin_client):
        assert (
            write_admin_client.post(
                "/api/admin/finance-hearings/dates", json=_DATE_PAYLOAD
            ).status_code
            == 201
        )

    def test_response_shape(self, write_admin_client):
        resp = write_admin_client.post(
            "/api/admin/finance-hearings/dates", json=_DATE_PAYLOAD
        ).json()
        for key in ("id", "hearing_date", "hearing_time", "is_full"):
            assert key in resp

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {k: v for k, v in _DATE_PAYLOAD.items() if k != "hearing_date"}
        assert (
            write_admin_client.post("/api/admin/finance-hearings/dates", json=bad).status_code
            == 422
        )


# ---------------------------------------------------------------------------
# PUT /api/admin/finance-hearings/dates/{id}
# ---------------------------------------------------------------------------


class TestUpdateFinanceDate:
    def _create_date(self, client) -> int:
        return client.post("/api/admin/finance-hearings/dates", json=_DATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        date_id = self._create_date(write_admin_client)
        assert (
            write_admin_client.put(
                f"/api/admin/finance-hearings/dates/{date_id}", json={"is_full": True}
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        date_id = self._create_date(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/finance-hearings/dates/{date_id}",
            json={"is_full": True, "location": "Changed"},
        )
        assert resp.json()["is_full"] is True
        assert resp.json()["location"] == "Changed"

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/finance-hearings/dates/999999", json={"is_full": True}
            ).status_code
            == 404
        )


# ---------------------------------------------------------------------------
# DELETE /api/admin/finance-hearings/dates/{id}
# ---------------------------------------------------------------------------


class TestDeleteFinanceDate:
    def _create_date(self, client) -> int:
        return client.post("/api/admin/finance-hearings/dates", json=_DATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        date_id = self._create_date(write_admin_client)
        assert (
            write_admin_client.delete(f"/api/admin/finance-hearings/dates/{date_id}").status_code
            == 204
        )

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.delete("/api/admin/finance-hearings/dates/999999").status_code == 404
        )

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/finance-hearings/dates/1").status_code in {
                    401,
                    403,
                    501,
                }
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
