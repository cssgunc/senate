"""Tests for staff input/output schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.staff import CreateStaffDTO, StaffDTO


class TestCreateStaffDTO:
    def test_valid(self):
        dto = CreateStaffDTO(
            first_name="Alex",
            last_name="Jones",
            title="Communications Director",
            email="ajones@unc.edu",
            display_order=1,
        )
        assert dto.display_order == 1

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            CreateStaffDTO(
                first_name="Alex",
                last_name="Jones",
                title="Director",
                email="not-an-email",
                display_order=1,
            )


class TestStaffDTO:
    def test_from_attributes(self):
        class FakeStaff:
            id = 1
            first_name = "Alex"
            last_name = "Jones"
            title = "Director"
            email = "ajones@unc.edu"
            photo_url = None

        dto = StaffDTO.model_validate(FakeStaff())
        assert dto.photo_url is None
