"""Integration tests for admin district CRUD routes (ticket #71)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint, create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin, Senator
from app.models.base import Base
from app.models.District import District

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


def _seed(engine) -> int:
    """Returns the ID of the seeded district."""
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(
        Admin(
            email="admin@unc.edu",
            first_name="Admin",
            last_name="User",
            pid="100000001",
            role="admin",
        )
    )
    db.flush()
    d = District(district_name="On-Campus", description="On-campus students")
    db.add(d)
    db.commit()
    district_id = d.id
    db.close()
    return district_id


def _seed_with_senator(engine) -> tuple[int, int]:
    """Returns (district_id, senator_id) for FK constraint testing."""
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add(
        Admin(
            email="admin@unc.edu",
            first_name="Admin",
            last_name="User",
            pid="100000001",
            role="admin",
        )
    )
    db.flush()
    d = District(district_name="Locked District", description=None)
    db.add(d)
    db.flush()
    s = Senator(
        first_name="Alice",
        last_name="Smith",
        email="asmith@unc.edu",
        district=d.id,
        is_active=True,
        session_number=35,
    )
    db.add(s)
    db.commit()
    ids = (d.id, s.id)
    db.close()
    return ids


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


_CREATE_PAYLOAD = {"district_name": "Graduate Students", "description": "Graduate student district"}


# ---------------------------------------------------------------------------
# GET /api/admin/districts
# ---------------------------------------------------------------------------


class TestListAdminDistricts:
    def test_returns_200(self, admin_read_client):
        assert admin_read_client.get("/api/admin/districts").status_code == 200

    def test_returns_list(self, admin_read_client):
        data = admin_read_client.get("/api/admin/districts").json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_response_shape(self, admin_read_client):
        item = admin_read_client.get("/api/admin/districts").json()[0]
        for key in ("id", "district_name", "description"):
            assert key in item

    def test_no_senator_field(self, admin_read_client):
        item = admin_read_client.get("/api/admin/districts").json()[0]
        assert "senator" not in item

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/districts").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# POST /api/admin/districts
# ---------------------------------------------------------------------------


class TestCreateAdminDistrict:
    def test_returns_201(self, write_admin_client):
        assert (
            write_admin_client.post("/api/admin/districts", json=_CREATE_PAYLOAD).status_code == 201
        )

    def test_response_shape(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/districts", json=_CREATE_PAYLOAD).json()
        for key in ("id", "district_name", "description"):
            assert key in resp

    def test_missing_name_returns_422(self, write_admin_client):
        assert (
            write_admin_client.post(
                "/api/admin/districts", json={"description": "No name"}
            ).status_code
            == 422
        )


# ---------------------------------------------------------------------------
# PUT /api/admin/districts/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminDistrict:
    def _create_district(self, client) -> int:
        return client.post("/api/admin/districts", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        district_id = self._create_district(write_admin_client)
        assert (
            write_admin_client.put(
                f"/api/admin/districts/{district_id}", json={"district_name": "Updated"}
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        district_id = self._create_district(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/districts/{district_id}", json={"district_name": "Changed"}
        )
        assert resp.json()["district_name"] == "Changed"

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/districts/999999", json={"district_name": "X"}
            ).status_code
            == 404
        )


# ---------------------------------------------------------------------------
# DELETE /api/admin/districts/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminDistrict:
    def _create_district(self, client) -> int:
        return client.post("/api/admin/districts", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        district_id = self._create_district(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/districts/{district_id}").status_code == 204

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/districts/999999").status_code == 404

    def test_returns_409_when_senator_linked(self):
        engine = _make_engine()
        district_id, _ = _seed_with_senator(engine)
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
                assert c.delete(f"/api/admin/districts/{district_id}").status_code == 409
        finally:
            _clear()
            Base.metadata.drop_all(bind=engine)
