"""Finance hearing schemas — input and output DTOs."""

from datetime import date, time

from pydantic import BaseModel, ConfigDict


class FinanceHearingDateDTO(BaseModel):
    id: int
    hearing_date: date
    hearing_time: time
    location: str | None
    description: str | None
    is_full: bool

    model_config = ConfigDict(from_attributes=True)


class FinanceHearingConfigDTO(BaseModel):
    is_active: bool
    season_start: date | None
    season_end: date | None
    dates: list[FinanceHearingDateDTO]

    model_config = ConfigDict(from_attributes=True)


class UpdateFinanceHearingConfigDTO(BaseModel):
    is_active: bool
    season_start: date | None
    season_end: date | None


class CreateFinanceHearingDateDTO(BaseModel):
    hearing_date: date
    hearing_time: time
    location: str | None
    description: str | None
