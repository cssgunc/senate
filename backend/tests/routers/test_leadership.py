"""Leadership router tests."""


# --- Tests ---
def test_get_all_active_leadership(client, seeded_leadership):
    response = client.get("/api/leadership/")
    assert response.status_code == 200
    data = response.json()

    # Only active records should be returned
    titles = [leader["title"] for leader in data]
    assert "Speaker" in titles
    assert "Whip" in titles
    assert "Minority Leader" not in titles


def test_get_leadership_by_session_number(client, seeded_leadership):
    response = client.get("/api/leadership/?session_number=2025")
    assert response.status_code == 200
    data = response.json()

    # Should return only records with session_number=2025
    assert all(leader["session_number"] == 2025 for leader in data)
    titles = [leader["title"] for leader in data]
    assert set(titles) == {"Speaker", "Whip"}


def test_get_leadership_by_id_success(client, seeded_leadership):
    leadership = seeded_leadership["records"][0]  # Speaker
    response = client.get(f"/api/leadership/{leadership.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == leadership.id
    assert data["title"] == leadership.title


def test_get_leadership_by_id_not_found(client):
    response = client.get("/api/leadership/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Leadership record not found"
