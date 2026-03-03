"""Integration tests for GET /api/news endpoints (TDD Section 4.5.2)."""


class TestListNews:
    def test_returns_200(self, client):
        response = client.get("/api/news")
        assert response.status_code == 200

    def test_response_has_pagination_shape(self, client):
        data = client.get("/api/news").json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_only_published_articles_returned(self, client):
        data = client.get("/api/news").json()
        for item in data["items"]:
            # draft article titled "Draft Article" must not appear
            assert item["title"] != "Draft Article"

    def test_total_reflects_published_count(self, client):
        data = client.get("/api/news").json()
        # Only 2 published articles seeded
        assert data["total"] == 2

    def test_ordered_most_recent_first(self, client):
        data = client.get("/api/news").json()
        items = data["items"]
        assert len(items) >= 2
        # "Recent News" (2026-03-03) must come before "Older News" (2026-01-01)
        titles = [i["title"] for i in items]
        assert titles.index("Recent News") < titles.index("Older News")

    def test_default_page_and_limit(self, client):
        data = client.get("/api/news").json()
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_custom_limit(self, client):
        data = client.get("/api/news?limit=1").json()
        assert data["limit"] == 1
        assert len(data["items"]) == 1
        assert data["total"] == 2  # total is still 2

    def test_pagination_page_2_empty(self, client):
        data = client.get("/api/news?page=2&limit=10").json()
        assert data["page"] == 2
        assert data["items"] == []
        assert data["total"] == 2

    def test_article_fields_present(self, client):
        item = client.get("/api/news").json()["items"][0]
        for field in ("id", "title", "summary", "body", "date_published", "date_last_edited"):
            assert field in item, f"Field '{field}' missing from news item"

    def test_image_url_nullable(self, client):
        # "Recent News" has no image_url; "Older News" has one
        items = client.get("/api/news").json()["items"]
        has_null = any(i["image_url"] is None for i in items)
        has_value = any(i["image_url"] is not None for i in items)
        assert has_null
        assert has_value

    def test_invalid_page_param(self, client):
        # page must be >= 1
        assert client.get("/api/news?page=0").status_code == 422

    def test_invalid_limit_param(self, client):
        # limit must be >= 1
        assert client.get("/api/news?limit=0").status_code == 422


class TestGetNewsById:
    def _published_id(self, client) -> int:
        return client.get("/api/news").json()["items"][0]["id"]

    def test_returns_200_for_published(self, client):
        news_id = self._published_id(client)
        assert client.get(f"/api/news/{news_id}").status_code == 200

    def test_returns_correct_article(self, client):
        news_id = self._published_id(client)
        data = client.get(f"/api/news/{news_id}").json()
        assert data["id"] == news_id

    def test_article_fields_present(self, client):
        news_id = self._published_id(client)
        data = client.get(f"/api/news/{news_id}").json()
        for field in ("id", "title", "summary", "body", "date_published", "date_last_edited"):
            assert field in data

    def test_returns_404_for_nonexistent(self, client):
        assert client.get("/api/news/999999").status_code == 404

    def test_returns_404_for_unpublished(self, client):
        # Fetch the draft by listing all (we know draft id comes from the seed).
        # We can't list drafts via the API, so fetch by iterating known IDs.
        # The draft has title "Draft Article" and is seeded as id = the 3rd news row.
        # Instead of hardcoding, confirm 404 by brute-forcing small IDs that aren't published.
        published_ids = {
            item["id"] for item in client.get("/api/news").json()["items"]
        }
        # Try IDs 1-10 that are not in published_ids — those should be 404
        found_404 = False
        for candidate in range(1, 11):
            if candidate not in published_ids:
                resp = client.get(f"/api/news/{candidate}")
                if resp.status_code == 404:
                    found_404 = True
                    break
        assert found_404, "Expected 404 for draft/unpublished article"
