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


def test_create_committee(admin_client, test_db):
    response = admin_client.post(
        "/api/admin/committees",
        json={
            "name": "New Committee",
            "description": "A fully new committee",
            "chair_name": "Chair Person",
            "chair_email": "chair@example.com",
            "is_active": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Committee"
    assert "id" in data
    assert len(data["members"]) == 0


def test_list_committees(admin_client, seeded_committees):
    response = admin_client.get("/api/admin/committees")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all("id" in committee for committee in data)
    assert all("members" in committee for committee in data)


def test_update_committee(admin_client, seeded_committees):
    committee = seeded_committees["committees"][0]
    response = admin_client.put(
        f"/api/admin/committees/{committee.id}",
        json={"name": "Updated Finance Committee", "is_active": False},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == committee.id
    assert data["name"] == "Updated Finance Committee"
    assert data["is_active"] is False
    assert len(data["members"]) == 2  # Members should still be there


def test_delete_committee(admin_client, test_db, seeded_committees):
    committee_to_delete = seeded_committees["committees"][1]  # Education Committee

    # Delete
    response = admin_client.delete(f"/api/admin/committees/{committee_to_delete.id}")
    assert response.status_code == 204

    # Verify
    get_response = admin_client.get(f"/api/committees/{committee_to_delete.id}")
    assert get_response.status_code == 404


def test_add_committee_member(admin_client, seeded_committees):
    committee = seeded_committees["committees"][1]  # Education Committee, has no members
    senator = seeded_committees["senators"][0]  # John Doe

    response = admin_client.post(
        f"/api/admin/committees/{committee.id}/members",
        json={"senator_id": senator.id, "role": "Chair"},
    )
    assert response.status_code == 201

    # Verify by fetching the committee if we had an admin read endpoint,
    # but we can try to add the exact same person to trigger the 409 Conflict.
    response_duplicate = admin_client.post(
        f"/api/admin/committees/{committee.id}/members",
        json={"senator_id": senator.id, "role": "Chair"},
    )
    assert response_duplicate.status_code == 409
    assert "already a member" in response_duplicate.json()["detail"]


def test_remove_committee_member(admin_client, test_db, seeded_committees):
    # m1 is John Doe in Finance Committee
    m1 = seeded_committees["memberships"][0]
    committee_id = m1.committee_id
    senator_id = m1.senator_id

    response = admin_client.delete(f"/api/admin/committees/{committee_id}/members/{senator_id}")
    assert response.status_code == 204

    # Verify deletion
    response_verify = admin_client.delete(
        f"/api/admin/committees/{committee_id}/members/{senator_id}"
    )
    assert response_verify.status_code == 404


def test_unauthenticated_create_rejected(client):
    response = client.post(
        "/api/admin/committees",
        json={
            "name": "New Committee",
            "description": "A fully new committee",
            "chair_name": "Chair Person",
            "chair_email": "chair@example.com",
            "is_active": True,
        },
    )
    assert response.status_code in {401, 403}


def test_staff_cannot_delete_committee(staff_client, seeded_committees):
    committee = seeded_committees["committees"][0]
    response = staff_client.delete(f"/api/admin/committees/{committee.id}")
    assert response.status_code == 403


def test_staff_cannot_remove_committee_member(staff_client, seeded_committees):
    m1 = seeded_committees["memberships"][0]
    response = staff_client.delete(
        f"/api/admin/committees/{m1.committee_id}/members/{m1.senator_id}"
    )
    assert response.status_code == 403
