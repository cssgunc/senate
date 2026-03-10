"""Integration tests for GET /api/pages/:slug (TDD Section 4.5.2)."""


class TestGetPage:
    def test_returns_200_for_existing_slug(self, client):
        assert client.get("/api/pages/powers-of-senate").status_code == 200

    def test_returns_correct_page(self, client):
        data = client.get("/api/pages/powers-of-senate").json()
        assert data["page_slug"] == "powers-of-senate"
        assert data["title"] == "Powers of the Senate"

    def test_page_fields_present(self, client):
        data = client.get("/api/pages/powers-of-senate").json()
        for field in ("id", "page_slug", "title", "body", "updated_at"):
            assert field in data, f"Field '{field}' missing from page"

    def test_body_not_empty(self, client):
        data = client.get("/api/pages/powers-of-senate").json()
        assert len(data["body"]) > 0

    def test_404_for_nonexistent_slug(self, client):
        assert client.get("/api/pages/this-page-does-not-exist").status_code == 404

    def test_404_response_has_detail(self, client):
        data = client.get("/api/pages/this-page-does-not-exist").json()
        assert "detail" in data
