"""Integration tests for GET /api/carousel (TDD Section 4.5.2)."""


class TestListCarousel:
    def test_returns_200(self, client):
        assert client.get("/api/carousel").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/carousel").json()
        assert isinstance(data, list)

    def test_only_active_slides(self, client):
        """Inactive slide (slide3) must not appear; only 2 active slides seeded."""
        data = client.get("/api/carousel").json()
        assert len(data) == 2
        assert all(s["is_active"] for s in data)

    def test_ordered_by_display_order(self, client):
        data = client.get("/api/carousel").json()
        orders = [s["display_order"] for s in data]
        assert orders == sorted(orders)

    def test_slide_fields_present(self, client):
        slide = client.get("/api/carousel").json()[0]
        for field in ("id", "image_url", "overlay_text", "link_url", "display_order", "is_active"):
            assert field in slide, f"Field '{field}' missing from carousel slide"

    def test_nullable_overlay_text_and_link_url(self, client):
        """slide2 has null overlay_text and link_url — must be returned as null, not cause error."""
        data = client.get("/api/carousel").json()
        nullish = [s for s in data if s["overlay_text"] is None]
        assert len(nullish) == 1
        assert nullish[0]["link_url"] is None

    def test_first_slide_has_text_and_link(self, client):
        data = client.get("/api/carousel").json()
        first = next(s for s in data if s["display_order"] == 1)
        assert first["overlay_text"] == "Welcome to Senate"
        assert first["link_url"] == "https://unc.edu"
