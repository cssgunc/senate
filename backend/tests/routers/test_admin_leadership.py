import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin


@pytest.fixture
def admin_client(client, test_db, seeded_admins):
    admin = seeded_admins["admin"]

    def _override_current_user():
        return test_db.query(Admin).filter(Admin.id == admin.id).first()

    app.dependency_overrides[get_current_user] = _override_current_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def staff_client(client, test_db, seeded_admins):
    staff = seeded_admins["user"]

    def _override_current_user():
        return test_db.query(Admin).filter(Admin.id == staff.id).first()

    app.dependency_overrides[get_current_user] = _override_current_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


def test_list_admin_leadership_returns_paginated(admin_client, seeded_leadership):
    response = admin_client.get("/api/admin/leadership")
    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"items", "total", "page", "limit"}
    assert data["total"] == 4
    assert len(data["items"]) == 4


def test_list_admin_leadership_filter_session_number(admin_client, seeded_leadership):
    response = admin_client.get("/api/admin/leadership?session_number=2025")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert all(item["session_number"] == 2025 for item in data["items"])


def test_create_admin_leadership(admin_client):
    response = admin_client.post(
        "/api/admin/leadership",
        json={
            "title": "Secretary",
            "first_name": "Taylor",
            "last_name": "Green",
            "email": "tgreen@example.com",
            "session_number": 2026,
            "is_active": True,
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Secretary"
    assert data["is_current"] is True
    assert data["session_number"] == 2026


def test_create_admin_leadership_invalid_senator_returns_404(admin_client):
    response = admin_client.post(
        "/api/admin/leadership",
        json={
            "senator_id": 999999,
            "title": "Secretary",
            "first_name": "Taylor",
            "last_name": "Green",
            "email": "tgreen@example.com",
            "session_number": 2026,
            "is_active": True,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Senator not found"


def test_update_admin_leadership_partial(admin_client, seeded_leadership):
    leader = seeded_leadership["records"][0]
    response = admin_client.put(
        f"/api/admin/leadership/{leader.id}",
        json={"title": "Updated Speaker"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Speaker"


def test_update_admin_leadership_invalid_senator_returns_404(admin_client, seeded_leadership):
    leader = seeded_leadership["records"][0]
    response = admin_client.put(
        f"/api/admin/leadership/{leader.id}",
        json={"senator_id": 999999},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Senator not found"


def test_update_admin_leadership_not_found(admin_client):
    response = admin_client.put(
        "/api/admin/leadership/999999",
        json={"title": "Updated Speaker"},
    )
    assert response.status_code == 404


def test_delete_admin_leadership(admin_client, seeded_leadership):
    leader = seeded_leadership["records"][0]

    delete_response = admin_client.delete(f"/api/admin/leadership/{leader.id}")
    assert delete_response.status_code == 204

    get_response = admin_client.get(f"/api/leadership/{leader.id}")
    assert get_response.status_code == 404


def test_staff_cannot_delete_leadership(staff_client, seeded_leadership):
    leader = seeded_leadership["records"][0]
    response = staff_client.delete(f"/api/admin/leadership/{leader.id}")
    assert response.status_code == 403


def test_unauthenticated_create_rejected(client):
    response = client.post(
        "/api/admin/leadership",
        json={
            "title": "No Auth",
            "first_name": "No",
            "last_name": "Auth",
            "email": "no.auth@example.com",
            "session_number": 2026,
            "is_active": True,
        },
    )
    assert response.status_code in {401, 403}


def test_unauthenticated_list_rejected(client):
    response = client.get("/api/admin/leadership")
    assert response.status_code in {401, 403}


def test_unauthenticated_update_rejected(client):
    response = client.put(
        "/api/admin/leadership/1",
        json={"title": "Blocked"},
    )
    assert response.status_code in {401, 403}


def test_unauthenticated_delete_rejected(client, seeded_leadership):
    leader = seeded_leadership["records"][0]
    response = client.delete(f"/api/admin/leadership/{leader.id}")
    assert response.status_code in {401, 403}
