"""Tests for legislation input/output schemas."""

from datetime import date

from app.schemas.legislation import (
    CreateLegislationActionDTO,
    CreateLegislationDTO,
    LegislationActionDTO,
)


class TestCreateLegislationDTO:
    def test_valid(self):
        dto = CreateLegislationDTO(
            title="Senate Resolution 1",
            bill_number="SR-001",
            session_number=50,
            sponsor_id=None,
            sponsor_name="Jane Doe",
            summary="A resolution",
            full_text="Resolved that...",
            status="Introduced",
            type="Resolution",
            date_introduced=date(2026, 1, 15),
        )
        assert dto.sponsor_id is None
        assert dto.date_introduced == date(2026, 1, 15)

    def test_with_sponsor_id(self):
        dto = CreateLegislationDTO(
            title="SR-002",
            bill_number="SR-002",
            session_number=50,
            sponsor_id=3,
            sponsor_name="John Smith",
            summary="Summary",
            full_text="Full text",
            status="Passed",
            type="Bill",
            date_introduced=date(2026, 2, 1),
        )
        assert dto.sponsor_id == 3


class TestCreateLegislationActionDTO:
    def test_valid(self):
        dto = CreateLegislationActionDTO(
            legislation_id=1,
            action_date=date(2026, 2, 10),
            description="Referred to committee",
            action_type="Referral",
        )
        assert dto.action_type == "Referral"


class TestLegislationActionDTO:
    def test_from_attributes(self):
        class FakeAction:
            id = 1
            action_date = date(2026, 2, 10)
            description = "Referred to committee"
            action_type = "Referral"

        dto = LegislationActionDTO.model_validate(FakeAction())
        assert dto.id == 1
