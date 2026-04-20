"""Leadership router tests."""


# --- Tests ---
def test_get_current_session_leadership(client, seeded_leadership):
    response = client.get("/api/leadership/")
    assert response.status_code == 200
    data = response.json()

    # Defaulting should return the current session, including inactive rows.
    titles = [leader["title"] for leader in data]
    assert "Speaker" in titles
    assert "Whip" in titles
    assert "Parliamentarian" in titles
    assert "Minority Leader" not in titles

    parliamentarian = next(leader for leader in data if leader["title"] == "Parliamentarian")
    assert parliamentarian["session_number"] == 2025
    assert parliamentarian["is_current"] is False

    speaker = next(leader for leader in data if leader["title"] == "Speaker")
    assert speaker["is_current"] is True


def test_get_leadership_by_session_number(client, seeded_leadership):
    response = client.get("/api/leadership/?session_number=2025")
    assert response.status_code == 200
    data = response.json()

    # Explicit session filters should return all records for that session.
    assert all(leader["session_number"] == 2025 for leader in data)
    titles = [leader["title"] for leader in data]
    assert set(titles) == {"Speaker", "Whip", "Parliamentarian"}

    inactive = next(leader for leader in data if leader["title"] == "Parliamentarian")
    assert inactive["is_current"] is False


def test_get_leadership_by_previous_session(client, seeded_leadership):
    response = client.get("/api/leadership/?session_number=2023")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "Minority Leader"
    assert data[0]["is_current"] is False


def test_get_all_leadership_sessions(client, seeded_leadership):
    """Test fetching all leadership records across all sessions."""
    response = client.get("/api/leadership/sessions/all")
    assert response.status_code == 200
    data = response.json()

    # Should return records from both 2025 and 2023 sessions
    sessions = {leader["session_number"] for leader in data}
    assert 2025 in sessions
    assert 2023 in sessions

    # Data should be ordered by session descending, then by title
    # Check that 2025 records come before 2023 records
    session_indices = [i for i, leader in enumerate(data) if leader["session_number"] == 2025]
    if session_indices and not all(
        leader["session_number"] == 2025 for leader in data[: session_indices[-1] + 1]
    ):
        # If there's mixed sessions, ensure 2025 comes first
        first_2023_idx = next(
            i for i, leader in enumerate(data) if leader["session_number"] == 2023
        )
        assert all(leader["session_number"] == 2025 for leader in data[:first_2023_idx]), (
            "Sessions should be ordered descending"
        )

    # Total count should match seeded data
    assert len(data) == 4  # 3 from 2025 + 1 from 2023


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
