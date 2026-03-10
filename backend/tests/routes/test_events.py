"""Integration tests for GET /api/events (TDD Section 4.5.2)."""

from datetime import datetime


class TestListEvents:
    def test_returns_200(self, client):
        assert client.get("/api/events").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/events").json()
        assert isinstance(data, list)

    def test_only_published_events(self, client):
        """Draft event must not appear; only 2 published events seeded."""
        data = client.get("/api/events").json()
        assert len(data) == 2
        assert all(e["title"] != "Draft Event" for e in data)

    def test_ordered_by_start_datetime(self, client):
        data = client.get("/api/events").json()
        starts = [e["start_datetime"] for e in data]
        assert starts == sorted(starts)

    def test_event_fields_present(self, client):
        event = client.get("/api/events").json()[0]
        for field in ("id", "title", "description", "start_datetime", "end_datetime", "location", "event_type"):
            assert field in event, f"Field '{field}' missing from event"

    def test_nullable_description(self, client):
        """Finance Hearing event has null description."""
        data = client.get("/api/events").json()
        null_desc = [e for e in data if e["description"] is None]
        assert len(null_desc) == 1
        assert null_desc[0]["title"] == "Finance Hearing"

    # --- start_date filter ---

    def test_filter_start_date(self, client):
        """start_date=2026-04-10 should exclude the April 1st meeting."""
        data = client.get("/api/events?start_date=2026-04-10").json()
        assert len(data) == 1
        assert data[0]["title"] == "Finance Hearing"

    def test_filter_start_date_inclusive(self, client):
        """Events on exactly start_date are included."""
        data = client.get("/api/events?start_date=2026-04-01").json()
        assert len(data) == 2

    # --- end_date filter ---

    def test_filter_end_date(self, client):
        """end_date=2026-04-05 should only return the April 1st meeting."""
        data = client.get("/api/events?end_date=2026-04-05").json()
        assert len(data) == 1
        assert data[0]["title"] == "General Body Meeting"

    def test_filter_end_date_inclusive(self, client):
        """Events on exactly end_date are included."""
        data = client.get("/api/events?end_date=2026-04-15").json()
        assert len(data) == 2

    # --- event_type filter ---

    def test_filter_by_event_type(self, client):
        data = client.get("/api/events?event_type=hearing").json()
        assert len(data) == 1
        assert data[0]["title"] == "Finance Hearing"

    def test_filter_by_event_type_meeting(self, client):
        data = client.get("/api/events?event_type=meeting").json()
        assert len(data) == 1
        assert data[0]["title"] == "General Body Meeting"

    def test_filter_nonexistent_type_returns_empty(self, client):
        data = client.get("/api/events?event_type=zzznotype").json()
        assert data == []

    # --- combined filters ---

    def test_combined_start_and_type_filter(self, client):
        data = client.get("/api/events?start_date=2026-04-10&event_type=hearing").json()
        assert len(data) == 1
        assert data[0]["title"] == "Finance Hearing"

    def test_date_range_no_results(self, client):
        data = client.get("/api/events?start_date=2026-06-01&end_date=2026-06-30").json()
        assert data == []
