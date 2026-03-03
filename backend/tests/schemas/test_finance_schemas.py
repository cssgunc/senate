"""Tests for finance hearing input/output schemas."""

from datetime import date, time

from app.schemas.finance import CreateFinanceHearingDateDTO, UpdateFinanceHearingConfigDTO


class TestUpdateFinanceHearingConfigDTO:
    def test_active_with_dates(self):
        dto = UpdateFinanceHearingConfigDTO(
            is_active=True,
            season_start=date(2026, 1, 1),
            season_end=date(2026, 5, 1),
        )
        assert dto.is_active is True
        assert dto.season_start == date(2026, 1, 1)

    def test_inactive_no_dates(self):
        dto = UpdateFinanceHearingConfigDTO(
            is_active=False,
            season_start=None,
            season_end=None,
        )
        assert dto.season_end is None


class TestCreateFinanceHearingDateDTO:
    def test_valid(self):
        dto = CreateFinanceHearingDateDTO(
            hearing_date=date(2026, 3, 10),
            hearing_time=time(14, 30),
            location="Pit",
            description="Spring hearing",
        )
        assert dto.hearing_time == time(14, 30)

    def test_optional_fields_none(self):
        dto = CreateFinanceHearingDateDTO(
            hearing_date=date(2026, 3, 10),
            hearing_time=time(9, 0),
            location=None,
            description=None,
        )
        assert dto.location is None
