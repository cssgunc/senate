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
from app.models import (
    Admin,
    AdminSections,
    AppConfig,
    BudgetData,
    CalendarEvent,
    Sections,
    StaticPageContent,
)
from app.models.base import Base
from app.utils.passwords import hash_password

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
        email="admin@unc.edu",
        first_name="Admin",
        last_name="User",
        onyen="user100000001",
        password_hash=hash_password("TestPassword123!"),
        role="admin",
    )
    staff_user = Admin(
        email="staff@unc.edu",
        first_name="Staff",
        last_name="User",
        onyen="user200000002",
        password_hash=hash_password("TestPassword123!"),
        role="staff",
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
    "onyen": "newuser",
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
        for key in ("id", "email", "onyen", "first_name", "last_name", "role"):
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
        for key in ("id", "email", "onyen", "role"):
            assert key in resp

    def test_duplicate_email_returns_400(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "onyen": "anotheruser"}
        write_admin_client.post("/api/admin/accounts", json=_CREATE_PAYLOAD)
        assert write_admin_client.post("/api/admin/accounts", json=bad).status_code == 400

    def test_invalid_onyen_returns_422(self, write_admin_client):
        bad = {**_CREATE_PAYLOAD, "onyen": "not allowed"}
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


# ---------------------------------------------------------------------------
# Last-admin protection
# ---------------------------------------------------------------------------


class TestLastAdminProtection:
    def _create_admin(self, client, onyen: str, email: str) -> int:
        return client.post(
            "/api/admin/accounts",
            json={**_CREATE_PAYLOAD, "onyen": onyen, "email": email, "role": "admin"},
        ).json()["id"]

    def test_admin_can_delete_another_admin(self, write_admin_client):
        other_admin_id = self._create_admin(write_admin_client, "other-admin", "other-admin@unc.edu")
        assert write_admin_client.delete(f"/api/admin/accounts/{other_admin_id}").status_code == 204

    def test_admin_can_demote_another_admin(self, write_admin_client):
        other_admin_id = self._create_admin(write_admin_client, "other-admin", "other-admin@unc.edu")
        resp = write_admin_client.put(
            f"/api/admin/accounts/{other_admin_id}", json={"role": "staff"}
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "staff"

    def test_cannot_demote_last_admin(self, write_admin_client, write_engine):
        db = sessionmaker(bind=write_engine)()
        admin = db.query(Admin).filter(Admin.email == "admin@unc.edu").first()
        db.close()
        resp = write_admin_client.put(f"/api/admin/accounts/{admin.id}", json={"role": "staff"})
        assert resp.status_code == 400

    def test_demoting_non_last_admin_succeeds(self, write_admin_client, write_engine):
        db = sessionmaker(bind=write_engine)()
        staff = db.query(Admin).filter(Admin.email == "staff@unc.edu").first()
        staff_id = staff.id
        db.close()

        promote = write_admin_client.put(
            f"/api/admin/accounts/{staff_id}", json={"role": "admin"}
        )
        assert promote.status_code == 200

        demote = write_admin_client.put(
            f"/api/admin/accounts/{staff_id}", json={"role": "staff"}
        )
        assert demote.status_code == 200


# ---------------------------------------------------------------------------
# Deleting an admin who has authored other records
# ---------------------------------------------------------------------------


class TestDeleteAdminAccountWithAuthoredContent:
    def _create_author_admin(self, client) -> int:
        return client.post(
            "/api/admin/accounts",
            json={**_CREATE_PAYLOAD, "onyen": "author-admin", "email": "author-admin@unc.edu", "role": "admin"},
        ).json()["id"]

    def test_deleting_admin_nulls_static_page_editor(self, write_admin_client, write_engine):
        author_id = self._create_author_admin(write_admin_client)

        Session = sessionmaker(bind=write_engine)
        db = Session()
        db.add(
            StaticPageContent(
                page_slug="test-page", title="Test", body="Body", last_edited_by=author_id
            )
        )
        db.commit()
        db.close()

        assert write_admin_client.delete(f"/api/admin/accounts/{author_id}").status_code == 204

        db = Session()
        page = db.query(StaticPageContent).filter(StaticPageContent.page_slug == "test-page").first()
        db.close()
        assert page is not None
        assert page.last_edited_by is None

    def test_deleting_admin_nulls_app_config_updater(self, write_admin_client, write_engine):
        author_id = self._create_author_admin(write_admin_client)

        Session = sessionmaker(bind=write_engine)
        db = Session()
        db.add(AppConfig(key="test_flag", value="true", updated_by=author_id))
        db.commit()
        db.close()

        assert write_admin_client.delete(f"/api/admin/accounts/{author_id}").status_code == 204

        db = Session()
        config = db.query(AppConfig).filter(AppConfig.key == "test_flag").first()
        db.close()
        assert config is not None
        assert config.updated_by is None

    def test_deleting_admin_nulls_budget_data_updater(self, write_admin_client, write_engine):
        author_id = self._create_author_admin(write_admin_client)

        Session = sessionmaker(bind=write_engine)
        db = Session()
        db.add(
            BudgetData(
                fiscal_year="2026",
                category="Test",
                amount=100,
                display_order=0,
                updated_by=author_id,
            )
        )
        db.commit()
        db.close()

        assert write_admin_client.delete(f"/api/admin/accounts/{author_id}").status_code == 204

        db = Session()
        entry = db.query(BudgetData).filter(BudgetData.category == "Test").first()
        db.close()
        assert entry is not None
        assert entry.updated_by is None

    def test_deleting_admin_nulls_calendar_event_creator(self, write_admin_client, write_engine):
        author_id = self._create_author_admin(write_admin_client)

        Session = sessionmaker(bind=write_engine)
        db = Session()
        from datetime import datetime

        db.add(
            CalendarEvent(
                title="Test Event",
                start_datetime=datetime(2026, 1, 1),
                end_datetime=datetime(2026, 1, 2),
                event_type="meeting",
                is_published=False,
                created_by=author_id,
            )
        )
        db.commit()
        db.close()

        assert write_admin_client.delete(f"/api/admin/accounts/{author_id}").status_code == 204

        db = Session()
        event = db.query(CalendarEvent).filter(CalendarEvent.title == "Test Event").first()
        db.close()
        assert event is not None
        assert event.created_by is None

    def test_deleting_admin_cascades_section_membership(self, write_admin_client, write_engine):
        author_id = self._create_author_admin(write_admin_client)

        Session = sessionmaker(bind=write_engine)
        db = Session()
        section = Sections(name="Test Section")
        db.add(section)
        db.flush()
        db.add(AdminSections(section_id=section.id, admin_id=author_id))
        db.commit()
        db.close()

        assert write_admin_client.delete(f"/api/admin/accounts/{author_id}").status_code == 204

        db = Session()
        membership = db.query(AdminSections).filter(AdminSections.admin_id == author_id).first()
        db.close()
        assert membership is None
