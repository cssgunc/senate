"""Integration tests for admin account management routes (ticket #71).

All routes are admin-role only — staff users should receive 403 on all endpoints.
"""

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
    staff_user = Admin(
        email="staff@unc.edu", first_name="Staff", last_name="User", pid="200000002", role="staff"
    )
    db.add_all([admin_user, staff_user])
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


_CREATE_PAYLOAD = {
    "email": "newuser@unc.edu",
    "pid": "300000003",
    "first_name": "New",
    "last_name": "User",
    "role": "staff",
}


# ---------------------------------------------------------------------------
# GET /api/admin/accounts
# ---------------------------------------------------------------------------


class TestListAdminAccounts:
    def test_returns_200(self, admin_read_client):
        assert admin_read_client.get("/api/admin/accounts").status_code == 200

    def test_pagination_shape(self, admin_read_client):
        data = admin_read_client.get("/api/admin/accounts").json()
        for key in ("items", "total", "page", "limit"):
            assert key in data

    def test_returns_both_accounts(self, admin_read_client):
        data = admin_read_client.get("/api/admin/accounts").json()
        assert data["total"] == 2

    def test_response_shape(self, admin_read_client):
        item = admin_read_client.get("/api/admin/accounts").json()["items"][0]
        for key in ("id", "email", "pid", "first_name", "last_name", "role"):
            assert key in item

    def test_staff_cannot_list(self, read_engine):
        TestSession = sessionmaker(bind=read_engine)

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
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/accounts").status_code == 403
        finally:
            _clear()

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/accounts").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# POST /api/admin/accounts
# ---------------------------------------------------------------------------


class TestCreateAdminAccount:
    def test_returns_201(self, write_admin_client):
        assert (
            write_admin_client.post("/api/admin/accounts", json=_CREATE_PAYLOAD).status_code == 201
        )

    def test_response_shape(self, write_admin_client):
        resp = write_admin_client.post("/api/admin/accounts", json=_CREATE_PAYLOAD).json()
        for key in ("id", "email", "pid", "role"):
            assert key in resp

    def test_duplicate_email_returns_400(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "pid": "400000004"}
        write_admin_client.post("/api/admin/accounts", json=_CREATE_PAYLOAD)
        assert write_admin_client.post("/api/admin/accounts", json=bad).status_code == 400

    def test_invalid_pid_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "pid": "123"}
        assert write_admin_client.post("/api/admin/accounts", json=bad).status_code == 422

    def test_invalid_role_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "role": "superadmin"}
        assert write_admin_client.post("/api/admin/accounts", json=bad).status_code == 422

    def test_staff_cannot_create(self, write_staff_client):
        assert (
            write_staff_client.post("/api/admin/accounts", json=_CREATE_PAYLOAD).status_code == 403
        )


# ---------------------------------------------------------------------------
# PUT /api/admin/accounts/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminAccount:
    def _create_account(self, client) -> int:
        return client.post("/api/admin/accounts", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        account_id = self._create_account(write_admin_client)
        assert (
            write_admin_client.put(
                f"/api/admin/accounts/{account_id}", json={"first_name": "Updated"}
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        account_id = self._create_account(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/accounts/{account_id}", json={"first_name": "Changed", "role": "admin"}
        )
        assert resp.json()["first_name"] == "Changed"
        assert resp.json()["role"] == "admin"

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.put(
                "/api/admin/accounts/999999", json={"first_name": "X"}
            ).status_code
            == 404
        )

    def test_staff_cannot_update(self, write_staff_client):
        assert (
            write_staff_client.put("/api/admin/accounts/1", json={"first_name": "X"}).status_code
            == 403
        )


# ---------------------------------------------------------------------------
# DELETE /api/admin/accounts/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminAccount:
    def _create_account(self, client) -> int:
        return client.post("/api/admin/accounts", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_204(self, write_admin_client):
        account_id = self._create_account(write_admin_client)
        assert write_admin_client.delete(f"/api/admin/accounts/{account_id}").status_code == 204

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/accounts/999999").status_code == 404

    def test_staff_cannot_delete(self, write_staff_client):
        assert write_staff_client.delete("/api/admin/accounts/1").status_code == 403

    def test_cannot_delete_self(self, write_admin_client, write_engine):
        db = sessionmaker(bind=write_engine)()
        admin = db.query(Admin).filter(Admin.email == "admin@unc.edu").first()
        db.close()
        assert write_admin_client.delete(f"/api/admin/accounts/{admin.id}").status_code == 400

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.delete("/api/admin/accounts/1").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved
