"""Tests for senator input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.senator import (
    CommitteeAssignmentDTO,
    CreateSenatorDTO,
    SenatorDTO,
    UpdateSenatorDTO,
)


class TestCreateSenatorDTO:
    def test_valid(self):
        dto = CreateSenatorDTO(
            first_name="Jane",
            last_name="Doe",
            email="jane@unc.edu",
            district_id=1,
            session_number=50,
        )
        assert dto.email == "jane@unc.edu"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CreateSenatorDTO(
                first_name="Jane",
                last_name="Doe",
                email="not-an-email",
                district_id=1,
                session_number=50,
            )


class TestUpdateSenatorDTO:
    def test_valid(self):
        dto = UpdateSenatorDTO(
            first_name="Jane",
            last_name="Doe",
            email="jane@unc.edu",
            district_id=1,
            is_active=False,
            session_number=50,
        )
        assert dto.is_active is False

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UpdateSenatorDTO(
                first_name="Jane",
                last_name="Doe",
                email="bad",
                district_id=1,
                is_active=True,
                session_number=50,
            )


class TestSenatorDTO:
    def test_from_attributes(self):
        class FakeSenator:
            id = 1
            first_name = "Jane"
            last_name = "Doe"
            email = "jane@unc.edu"
            headshot_url = None
            district_id = 2
            is_active = True
            session_number = 50
            committees = []

        dto = SenatorDTO.model_validate(FakeSenator())
        assert dto.id == 1
        assert dto.headshot_url is None
        assert dto.committees == []


class TestCommitteeAssignmentDTO:
    def test_valid(self):
        dto = CommitteeAssignmentDTO(committee_id=1, committee_name="Finance", role="Member")
        assert dto.committee_name == "Finance"
