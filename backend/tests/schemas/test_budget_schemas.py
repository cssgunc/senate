"""Tests for budget data input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.budget import BudgetDataDTO, CreateBudgetDataDTO


class TestCreateBudgetDataDTO:
    def test_valid(self):
        dto = CreateBudgetDataDTO(
            fiscal_year="2025-2026",
            category="Operations",
            amount=5000.0,
            description=None,
            parent_category_id=None,
            display_order=1,
        )
        assert dto.amount == 5000.0

    def test_amount_zero_invalid(self):
        with pytest.raises(ValidationError, match="Amount must be positive"):
            CreateBudgetDataDTO(
                fiscal_year="2025-2026",
                category="Operations",
                amount=0.0,
                description=None,
                parent_category_id=None,
                display_order=1,
            )

    def test_amount_negative_invalid(self):
        with pytest.raises(ValidationError, match="Amount must be positive"):
            CreateBudgetDataDTO(
                fiscal_year="2025-2026",
                category="Operations",
                amount=-100.0,
                description=None,
                parent_category_id=None,
                display_order=1,
            )

    def test_optional_fields_none(self):
        dto = CreateBudgetDataDTO(
            fiscal_year="2025-2026",
            category="Operations",
            amount=1.0,
            description=None,
            parent_category_id=None,
            display_order=0,
        )
        assert dto.parent_category_id is None


class TestBudgetDataDTO:
    def test_self_referential_children(self):
        dto = BudgetDataDTO(
            id=1,
            fiscal_year="2025-2026",
            category="Operations",
            amount=10000.0,
            description=None,
            children=[
                BudgetDataDTO(
                    id=2,
                    fiscal_year="2025-2026",
                    category="Supplies",
                    amount=2000.0,
                    description=None,
                    children=[],
                )
            ],
        )
        assert len(dto.children) == 1
        assert dto.children[0].category == "Supplies"
