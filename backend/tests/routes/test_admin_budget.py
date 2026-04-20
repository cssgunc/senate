"""Integration tests for admin budget CRUD routes (ticket #71)."""

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
from app.models.BudgetData import BudgetData

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


def _seed(engine) -> tuple[int, int]:
    """Returns (parent_id, child_id) of seeded budget rows."""
    Session = sessionmaker(bind=engine)
    db = Session()
    admin_user = Admin(
        email="admin@unc.edu", first_name="Admin", last_name="User", pid="100000001", role="admin"
    )
    db.add(admin_user)
    db.flush()
    parent = BudgetData(
        fiscal_year="FY2026",
        category="Operations",
        amount=100000.00,
        description=None,
        parent_category_id=None,
        display_order=1,
        updated_by=admin_user.id,
    )
    db.add(parent)
    db.flush()
    child = BudgetData(
        fiscal_year="FY2026",
        category="Salaries",
        amount=60000.00,
        description=None,
        parent_category_id=parent.id,
        display_order=2,
        updated_by=admin_user.id,
    )
    db.add(child)
    db.commit()
    ids = (parent.id, child.id)
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
    "fiscal_year": "FY2026",
    "category": "Supplies",
    "amount": 5000.00,
    "description": "Office supplies",
    "parent_category_id": None,
    "display_order": 10,
}


# ---------------------------------------------------------------------------
# GET /api/admin/budget
# ---------------------------------------------------------------------------


class TestListAdminBudget:
    def test_returns_200(self, write_admin_client):
        assert write_admin_client.get("/api/admin/budget").status_code == 200

    def test_returns_list(self, write_admin_client):
        data = write_admin_client.get("/api/admin/budget").json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_fiscal_year_filter(self, write_admin_client):
        data = write_admin_client.get("/api/admin/budget?fiscal_year=FY2026").json()
        assert all(r["fiscal_year"] == "FY2026" for r in data)

    def test_unknown_fiscal_year_returns_empty(self, write_admin_client):
        data = write_admin_client.get("/api/admin/budget?fiscal_year=FY1900").json()
        assert data == []

    def test_response_shape(self, write_admin_client):
        item = write_admin_client.get("/api/admin/budget").json()[0]
        for key in ("id", "fiscal_year", "category", "amount", "display_order"):
            assert key in item

    def test_unauthenticated_rejected(self):
        saved = app.dependency_overrides.pop(get_current_user, None)
        try:
            with TestClient(app) as c:
                assert c.get("/api/admin/budget").status_code in {401, 403, 501}
        finally:
            if saved:
                app.dependency_overrides[get_current_user] = saved


# ---------------------------------------------------------------------------
# POST /api/admin/budget
# ---------------------------------------------------------------------------


class TestCreateAdminBudget:
    def test_returns_201(self, write_admin_client):
        assert write_admin_client.post("/api/admin/budget", json=_CREATE_PAYLOAD).status_code == 201

    def test_response_contains_id(self, write_admin_client):
        assert "id" in write_admin_client.post("/api/admin/budget", json=_CREATE_PAYLOAD).json()

    def test_invalid_parent_returns_404(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "parent_category_id": 999999}
        assert write_admin_client.post("/api/admin/budget", json=bad).status_code == 404

    def test_zero_amount_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "amount": 0}
        assert write_admin_client.post("/api/admin/budget", json=bad).status_code == 422

    def test_missing_required_field_returns_422(self, write_admin_client):
        bad = {k: v for k, v in _CREATE_PAYLOAD.items() if k != "fiscal_year"}
        assert write_admin_client.post("/api/admin/budget", json=bad).status_code == 422


# ---------------------------------------------------------------------------
# PUT /api/admin/budget/{id}
# ---------------------------------------------------------------------------


class TestUpdateAdminBudget:
    def _create_entry(self, client) -> int:
        return client.post("/api/admin/budget", json=_CREATE_PAYLOAD).json()["id"]

    def test_returns_200(self, write_admin_client):
        entry_id = self._create_entry(write_admin_client)
        assert (
            write_admin_client.put(
                f"/api/admin/budget/{entry_id}", json={"category": "Updated"}
            ).status_code
            == 200
        )

    def test_fields_updated(self, write_admin_client):
        entry_id = self._create_entry(write_admin_client)
        resp = write_admin_client.put(f"/api/admin/budget/{entry_id}", json={"category": "Changed"})
        assert resp.json()["category"] == "Changed"

    def test_self_parent_returns_400(self, write_admin_client):
        entry_id = self._create_entry(write_admin_client)
        resp = write_admin_client.put(
            f"/api/admin/budget/{entry_id}", json={"parent_category_id": entry_id}
        )
        assert resp.status_code == 400

    def test_returns_404_for_missing(self, write_admin_client):
        assert (
            write_admin_client.put("/api/admin/budget/999999", json={"category": "X"}).status_code
            == 404
        )


# ---------------------------------------------------------------------------
# DELETE /api/admin/budget/{id}
# ---------------------------------------------------------------------------


class TestDeleteAdminBudget:
    def test_returns_204_for_leaf(self, write_engine_with_ids):
        engine, (parent_id, child_id) = write_engine_with_ids
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
                assert c.delete(f"/api/admin/budget/{child_id}").status_code == 204
        finally:
            _clear()

    def test_returns_409_for_parent_with_children(self, write_engine_with_ids):
        engine, (parent_id, child_id) = write_engine_with_ids
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
                assert c.delete(f"/api/admin/budget/{parent_id}").status_code == 409
        finally:
            _clear()

    def test_returns_404_for_missing(self, write_admin_client):
        assert write_admin_client.delete("/api/admin/budget/999999").status_code == 404
