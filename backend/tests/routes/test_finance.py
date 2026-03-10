"""Integration tests for GET /api/finance-hearings (TDD Section 4.5.2)."""


class TestGetFinanceHearings:
    def test_returns_200(self, client):
        assert client.get("/api/finance-hearings").status_code == 200

    def test_returns_config_fields(self, client):
        data = client.get("/api/finance-hearings").json()
        for field in ("is_active", "season_start", "season_end", "dates"):
            assert field in data, f"Field '{field}' missing from finance hearing config"

    def test_active_config(self, client):
        data = client.get("/api/finance-hearings").json()
        assert data["is_active"] is True

    def test_season_dates_present(self, client):
        data = client.get("/api/finance-hearings").json()
        assert data["season_start"] == "2026-01-15"
        assert data["season_end"] == "2026-05-15"

    def test_active_config_includes_dates(self, client):
        """Active config should include all 2 seeded hearing dates."""
        data = client.get("/api/finance-hearings").json()
        assert isinstance(data["dates"], list)
        assert len(data["dates"]) == 2

    def test_date_fields_present(self, client):
        data = client.get("/api/finance-hearings").json()
        date_item = data["dates"][0]
        for field in ("id", "hearing_date", "hearing_time", "location", "description", "is_full"):
            assert field in date_item, f"Field '{field}' missing from hearing date"

    def test_nullable_description(self, client):
        """Second hearing date has null description — must be returned as null."""
        data = client.get("/api/finance-hearings").json()
        has_null_desc = any(d["description"] is None for d in data["dates"])
        assert has_null_desc

    def test_is_full_flag(self, client):
        """Second hearing date is marked full."""
        data = client.get("/api/finance-hearings").json()
        full_dates = [d for d in data["dates"] if d["is_full"]]
        assert len(full_dates) == 1
