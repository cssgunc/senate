"""Integration tests for GET /api/staff (TDD Section 4.5.2)."""


class TestListStaff:
    def test_returns_200(self, client):
        assert client.get("/api/staff").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/staff").json()
        assert isinstance(data, list)

    def test_only_active_staff_returned(self, client):
        """3 staff seeded (2 active, 1 inactive); only 2 should be returned."""
        data = client.get("/api/staff").json()
        assert len(data) == 2

    def test_inactive_staff_excluded(self, client):
        data = client.get("/api/staff").json()
        names = {s["first_name"] for s in data}
        assert "Inactive" not in names

    def test_ordered_by_display_order(self, client):
        data = client.get("/api/staff").json()
        assert data[0]["first_name"] == "First"
        assert data[1]["first_name"] == "Second"

    def test_staff_fields_present(self, client):
        staff = client.get("/api/staff").json()[0]
        for field in ("id", "first_name", "last_name", "title", "email", "photo_url"):
            assert field in staff, f"Field '{field}' missing from staff"

    def test_photo_url_nullable(self, client):
        """Staff seeded without photo_url; it should default to null."""
        data = client.get("/api/staff").json()
        assert all(s["photo_url"] is None for s in data)
