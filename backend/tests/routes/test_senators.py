"""Integration tests for GET /api/senators endpoints (TDD Section 4.5.2)."""


class TestListSenators:
    def test_returns_200(self, client):
        assert client.get("/api/senators").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/senators").json()
        assert isinstance(data, list)

    def test_defaults_to_active_senators_in_current_session(self, client):
        """Only active senators from session 35 (the highest seeded session) are returned."""
        data = client.get("/api/senators").json()
        # Seed has 2 active session-35 senators: Alice Smith, Bob Jones
        assert len(data) == 2
        names = {s["first_name"] for s in data}
        assert "Alice" in names
        assert "Bob" in names

    def test_inactive_senator_excluded_by_default(self, client):
        """Carol Lee is inactive — must not appear in the default listing."""
        data = client.get("/api/senators").json()
        names = {s["first_name"] for s in data}
        assert "Carol" not in names

    def test_old_session_senator_excluded_by_default(self, client):
        """Dan Brown is session 34 — must not appear when current session is 35."""
        data = client.get("/api/senators").json()
        names = {s["first_name"] for s in data}
        assert "Dan" not in names

    def test_senator_fields_present(self, client):
        senator = client.get("/api/senators").json()[0]
        for field in ("id", "first_name", "last_name", "email", "is_active", "session_number"):
            assert field in senator, f"Field '{field}' missing from senator"

    def test_committees_field_present(self, client):
        """Each senator should have a committees list (may be empty)."""
        for senator in client.get("/api/senators").json():
            assert "committees" in senator
            assert isinstance(senator["committees"], list)

    # --- search filter ---

    def test_search_by_first_name(self, client):
        data = client.get("/api/senators?search=alice").json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Alice"

    def test_search_by_last_name(self, client):
        data = client.get("/api/senators?search=jones").json()
        assert len(data) == 1
        assert data[0]["last_name"] == "Jones"

    def test_search_case_insensitive(self, client):
        upper = client.get("/api/senators?search=ALICE").json()
        lower = client.get("/api/senators?search=alice").json()
        assert len(upper) == len(lower) == 1

    def test_search_partial_match(self, client):
        # "Smi" should match "Smith"
        data = client.get("/api/senators?search=Smi").json()
        assert any(s["last_name"] == "Smith" for s in data)

    def test_search_no_match_returns_empty(self, client):
        data = client.get("/api/senators?search=zzznomatch").json()
        assert data == []

    # --- district_id filter ---

    def test_filter_by_district_id(self, client):
        senators = client.get("/api/senators").json()
        # Find a district_id that exists
        district_id = senators[0]["district_id"]
        filtered = client.get(f"/api/senators?district_id={district_id}").json()
        assert all(s["district_id"] == district_id for s in filtered)
        assert len(filtered) >= 1

    def test_filter_by_nonexistent_district_returns_empty(self, client):
        data = client.get("/api/senators?district_id=999999").json()
        assert data == []

    # --- committee filter ---

    def test_filter_by_committee(self, client):
        """Filtering by Finance Committee ID should return Alice and Bob (both members)."""
        senators = client.get("/api/senators").json()
        # Alice is in Finance; retrieve her committees to get finance committee_id
        alice = next(s for s in senators if s["first_name"] == "Alice")
        finance_committee_id = alice["committees"][0]["committee_id"]

        filtered = client.get(f"/api/senators?committee={finance_committee_id}").json()
        names = {s["first_name"] for s in filtered}
        # Both Alice (Chair) and Bob (Member) are in Finance
        assert "Alice" in names
        assert "Bob" in names

    def test_filter_by_nonexistent_committee_returns_empty(self, client):
        data = client.get("/api/senators?committee=999999").json()
        assert data == []

    # --- session filter ---

    def test_filter_by_session(self, client):
        data = client.get("/api/senators?session=35").json()
        assert all(s["session_number"] == 35 for s in data)

    def test_filter_by_old_session_returns_active_senators_of_that_session(self, client):
        # Session 34 has Dan Brown (active in that session)
        data = client.get("/api/senators?session=34").json()
        assert len(data) == 1
        assert data[0]["first_name"] == "Dan"

    # --- committee data on senator ---

    def test_senator_committee_assignments(self, client):
        senators = client.get("/api/senators").json()
        alice = next(s for s in senators if s["first_name"] == "Alice")
        assert len(alice["committees"]) == 1
        assert alice["committees"][0]["committee_name"] == "Finance Committee"
        assert alice["committees"][0]["role"] == "Chair"

    def test_senator_multiple_committee_assignments(self, client):
        senators = client.get("/api/senators").json()
        bob = next(s for s in senators if s["first_name"] == "Bob")
        assert len(bob["committees"]) == 2


class TestGetSenatorById:
    def _alice_id(self, client) -> int:
        senators = client.get("/api/senators").json()
        return next(s["id"] for s in senators if s["first_name"] == "Alice")

    def test_returns_200(self, client):
        senator_id = self._alice_id(client)
        assert client.get(f"/api/senators/{senator_id}").status_code == 200

    def test_returns_correct_senator(self, client):
        senator_id = self._alice_id(client)
        data = client.get(f"/api/senators/{senator_id}").json()
        assert data["id"] == senator_id
        assert data["first_name"] == "Alice"

    def test_includes_committee_assignments(self, client):
        senator_id = self._alice_id(client)
        data = client.get(f"/api/senators/{senator_id}").json()
        assert "committees" in data
        assert isinstance(data["committees"], list)
        assert len(data["committees"]) >= 1

    def test_committee_assignment_fields(self, client):
        senator_id = self._alice_id(client)
        data = client.get(f"/api/senators/{senator_id}").json()
        assignment = data["committees"][0]
        assert "committee_id" in assignment
        assert "committee_name" in assignment
        assert "role" in assignment

    def test_returns_404_for_nonexistent(self, client):
        assert client.get("/api/senators/999999").status_code == 404

    def test_can_fetch_senator_from_old_session(self, client):
        """Detail endpoint returns any senator by id, regardless of session."""
        # Dan Brown is session 34 — fetchable by ID even though filtered out by default list
        all_senators = client.get("/api/senators?session=34").json()
        dan_id = next(s["id"] for s in all_senators if s["first_name"] == "Dan")
        assert client.get(f"/api/senators/{dan_id}").status_code == 200
