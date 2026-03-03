"""Tests for committee input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.committee import AssignCommitteeMemberDTO, CreateCommitteeDTO


class TestCreateCommitteeDTO:
    def test_valid(self):
        dto = CreateCommitteeDTO(
            name="Finance",
            description="Handles budget",
            chair_senator_id=None,
            chair_name="John Smith",
            chair_email="jsmith@unc.edu",
        )
        assert dto.chair_senator_id is None

    def test_with_chair_senator_id(self):
        dto = CreateCommitteeDTO(
            name="Finance",
            description="Handles budget",
            chair_senator_id=5,
            chair_name="John Smith",
            chair_email="jsmith@unc.edu",
        )
        assert dto.chair_senator_id == 5

    def test_invalid_chair_email(self):
        with pytest.raises(ValidationError):
            CreateCommitteeDTO(
                name="Finance",
                description="Handles budget",
                chair_senator_id=None,
                chair_name="John Smith",
                chair_email="not-an-email",
            )


class TestAssignCommitteeMemberDTO:
    def test_valid(self):
        dto = AssignCommitteeMemberDTO(senator_id=3, role="Vice Chair")
        assert dto.role == "Vice Chair"
