import pytest
from fastapi.testclient import TestClient

from app.main import app  # your FastAPI app


@pytest.fixture
def client(test_db):
    return TestClient(app)

# --- Tests ---
def test_get_committee_by_id(client, seeded_committees):
    committee = seeded_committees["committees"][0]

    response = client.get(f"/api/committees/{committee.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == committee.id
    assert data["name"] == "Finance Committee"
    assert len(data["members"]) == 2
    roles = {c["role"] for m in data["members"] for c in m["committees"]}
    assert roles == {"Chair", "Member"}

def test_get_committee_not_found(client, test_db):
    response = client.get("/api/committees/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Committee not found"

def test_get_all_active_committees(client, seeded_committees):
    response = client.get("/api/committees/")
    assert response.status_code == 200

    data = response.json()
    # Only active committees
    names = [c["name"] for c in data]
    assert "Finance Committee" in names
    assert "Education Committee" not in names
