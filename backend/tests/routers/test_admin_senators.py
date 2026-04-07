import pytest

from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin, Leadership, Senator


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


def test_list_admin_senators_returns_paginated(admin_client, seeded_committees):
    response = admin_client.get("/api/admin/senators")
    assert response.status_code == 200

    data = response.json()
    assert set(data.keys()) == {"items", "total", "page", "limit"}
    assert data["total"] == 2
    assert data["page"] == 1
    assert data["limit"] == 20
    assert len(data["items"]) == 2


def test_list_admin_senators_filters(admin_client, test_db, seeded_committees):
    inactive = Senator(
        first_name="Inactive",
        last_name="Member",
        email="inactive@example.com",
        district=1,
        is_active=False,
        session_number=2025,
    )
    test_db.add(inactive)
    test_db.commit()

    active_response = admin_client.get("/api/admin/senators?is_active=true")
    assert active_response.status_code == 200
    assert all(item["is_active"] is True for item in active_response.json()["items"])

    session_response = admin_client.get("/api/admin/senators?session=2016")
    assert session_response.status_code == 200
    assert all(item["session_number"] == 2016 for item in session_response.json()["items"])


def test_create_admin_senator(admin_client, seeded_committees):
    district_id = seeded_committees["senators"][0].district
    response = admin_client.post(
        "/api/admin/senators",
        json={
            "first_name": "New",
            "last_name": "Senator",
            "email": "new.senator@example.com",
            "district_id": district_id,
            "session_number": 2026,
        },
    )
    assert response.status_code == 201

    data = response.json()
    assert data["first_name"] == "New"
    assert data["district_id"] == district_id
    assert data["session_number"] == 2026


def test_create_admin_senator_invalid_district_returns_404(admin_client):
    response = admin_client.post(
        "/api/admin/senators",
        json={
            "first_name": "Bad",
            "last_name": "District",
            "email": "bad.district@example.com",
            "district_id": 999999,
            "session_number": 2026,
        },
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "District not found"


def test_update_admin_senator_partial(admin_client, seeded_committees):
    senator = seeded_committees["senators"][0]
    response = admin_client.put(
        f"/api/admin/senators/{senator.id}",
        json={"is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_update_admin_senator_invalid_district_returns_404(admin_client, seeded_committees):
    senator = seeded_committees["senators"][0]
    response = admin_client.put(
        f"/api/admin/senators/{senator.id}",
        json={"district_id": 999999},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "District not found"


def test_update_admin_senator_not_found(admin_client):
    response = admin_client.put(
        "/api/admin/senators/999999",
        json={"is_active": False},
    )
    assert response.status_code == 404


def test_delete_admin_senator(admin_client, seeded_committees):
    senator = seeded_committees["senators"][1]

    delete_response = admin_client.delete(f"/api/admin/senators/{senator.id}")
    assert delete_response.status_code == 204

    get_response = admin_client.get(f"/api/senators/{senator.id}")
    assert get_response.status_code == 404


def test_delete_admin_senator_conflict_when_linked_leadership(
    admin_client, test_db, seeded_committees
):
    senator = seeded_committees["senators"][0]
    leader = Leadership(
        senator_id=senator.id,
        title="Speaker",
        first_name=senator.first_name,
        last_name=senator.last_name,
        email=senator.email,
        headshot_url=None,
        is_active=True,
        session_number=2025,
    )
    test_db.add(leader)
    test_db.commit()

    response = admin_client.delete(f"/api/admin/senators/{senator.id}")
    assert response.status_code == 409
    assert "update or delete leadership first" in response.json()["detail"]


def test_staff_cannot_delete_senator(staff_client, seeded_committees):
    senator = seeded_committees["senators"][0]
    response = staff_client.delete(f"/api/admin/senators/{senator.id}")
    assert response.status_code == 403


def test_unauthenticated_create_rejected(client):
    response = client.post(
        "/api/admin/senators",
        json={
            "first_name": "No",
            "last_name": "Auth",
            "email": "no.auth@example.com",
            "district_id": 1,
            "session_number": 2026,
        },
    )
    assert response.status_code in {401, 403}


def test_unauthenticated_list_rejected(client):
    response = client.get("/api/admin/senators")
    assert response.status_code in {401, 403}


def test_unauthenticated_update_rejected(client):
    response = client.put(
        "/api/admin/senators/1",
        json={"is_active": False},
    )
    assert response.status_code in {401, 403}


def test_unauthenticated_delete_rejected(client, seeded_committees):
    senator = seeded_committees["senators"][0]
    response = client.delete(f"/api/admin/senators/{senator.id}")
    assert response.status_code in {401, 403}
