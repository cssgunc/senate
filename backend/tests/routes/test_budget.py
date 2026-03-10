"""Integration tests for GET /api/budget (TDD Section 4.5.2)."""

from app.models import Admin
from app.models.BudgetData import BudgetData


class TestListBudget:
    def test_returns_200(self, client):
        assert client.get("/api/budget").status_code == 200

    def test_returns_list(self, client):
        data = client.get("/api/budget").json()
        assert isinstance(data, list)

    def test_defaults_to_most_recent_fiscal_year(self, client):
        """FY2026 is more recent than FY2025; default should return FY2026 rows only."""
        data = client.get("/api/budget").json()
        assert len(data) >= 1
        assert all(item["fiscal_year"] == "FY2026" for item in data)

    def test_top_level_only_at_root(self, client):
        """Only parent-level items (parent_category_id=NULL) appear at the root."""
        data = client.get("/api/budget").json()
        # One parent seeded for FY2026
        assert len(data) == 1
        assert data[0]["category"] == "Operations"

    def test_hierarchical_children(self, client):
        """'Operations' parent has 2 children: Salaries and Supplies."""
        data = client.get("/api/budget").json()
        parent = data[0]
        assert isinstance(parent["children"], list)
        assert len(parent["children"]) == 2
        child_names = {c["category"] for c in parent["children"]}
        assert "Salaries" in child_names
        assert "Supplies" in child_names

    def test_children_have_empty_children_list(self, client):
        """Leaf nodes must have an empty children list (not missing the field)."""
        data = client.get("/api/budget").json()
        for child in data[0]["children"]:
            assert "children" in child
            assert child["children"] == []

    def test_filter_by_fiscal_year(self, client):
        data = client.get("/api/budget?fiscal_year=FY2025").json()
        assert len(data) == 1
        assert data[0]["fiscal_year"] == "FY2025"
        assert data[0]["category"] == "Old Operations"

    def test_filter_older_year_excludes_newer(self, client):
        data = client.get("/api/budget?fiscal_year=FY2025").json()
        assert all(item["fiscal_year"] == "FY2025" for item in data)

    def test_nonexistent_fiscal_year_returns_empty(self, client):
        data = client.get("/api/budget?fiscal_year=FY1900").json()
        assert data == []

    def test_budget_fields_present(self, client):
        data = client.get("/api/budget").json()
        item = data[0]
        for field in ("id", "fiscal_year", "category", "amount", "description", "children"):
            assert field in item, f"Field '{field}' missing from budget item"

    def test_amount_is_numeric(self, client):
        data = client.get("/api/budget").json()
        assert isinstance(data[0]["amount"], (int, float))

    def test_default_year_not_lexicographic(self, client, db_session):
        """Adding FY9 should not override FY2026 as the default year."""
        admin = db_session.query(Admin).first()
        db_session.add(
            BudgetData(
                fiscal_year="FY9",
                category="Legacy",
                amount=1.00,
                description=None,
                parent_category_id=None,
                display_order=99,
                updated_by=admin.id,
            )
        )
        db_session.commit()

        data = client.get("/api/budget").json()
        assert len(data) >= 1
        assert all(item["fiscal_year"] == "FY2026" for item in data)
