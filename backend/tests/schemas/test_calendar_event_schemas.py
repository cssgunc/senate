"""Tests for calendar event input schemas."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.calendar_event import CreateCalendarEventDTO


class TestCreateCalendarEventDTO:
    def test_valid(self):
        dto = CreateCalendarEventDTO(
            title="Senate Meeting",
            description="Monthly meeting",
            start_datetime=datetime(2026, 3, 10, 14, 0),
            end_datetime=datetime(2026, 3, 10, 15, 0),
            location="Pit",
            event_type="Meeting",
        )
        assert dto.title == "Senate Meeting"

    def test_end_before_start_invalid(self):
        with pytest.raises(ValidationError, match="end_datetime must be after start_datetime"):
            CreateCalendarEventDTO(
                title="Senate Meeting",
                description=None,
                start_datetime=datetime(2026, 3, 10, 15, 0),
                end_datetime=datetime(2026, 3, 10, 14, 0),
                location=None,
                event_type="Meeting",
            )

    def test_end_equal_to_start_invalid(self):
        with pytest.raises(ValidationError, match="end_datetime must be after start_datetime"):
            CreateCalendarEventDTO(
                title="Senate Meeting",
                description=None,
                start_datetime=datetime(2026, 3, 10, 14, 0),
                end_datetime=datetime(2026, 3, 10, 14, 0),
                location=None,
                event_type="Meeting",
            )

    def test_optional_fields_none(self):
        dto = CreateCalendarEventDTO(
            title="Event",
            description=None,
            start_datetime=datetime(2026, 3, 10, 9, 0),
            end_datetime=datetime(2026, 3, 10, 10, 0),
            location=None,
            event_type="Other",
        )
        assert dto.description is None
        assert dto.location is None
