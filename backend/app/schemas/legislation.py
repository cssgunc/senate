"""Legislation schemas — input and output DTOs."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class LegislationActionDTO(BaseModel):
    id: int
    action_date: date
    description: str
    action_type: str

    model_config = ConfigDict(from_attributes=True)


class LegislationListDTO(BaseModel):
    id: int
    title: str
    bill_number: str
    session_number: int
    sponsor_name: str
    summary: str
    full_text: str
    status: str
    type: str
    date_introduced: date
    date_last_action: date

    model_config = ConfigDict(from_attributes=True)


class LegislationDetailDTO(LegislationListDTO):
    actions: list[LegislationActionDTO]


class LegislationDTO(LegislationDetailDTO):
    """Backward-compatible alias for detailed legislation responses."""


class CreateLegislationDTO(BaseModel):
    title: str
    bill_number: str
    session_number: int
    sponsor_id: int | None
    sponsor_name: str
    summary: str
    full_text: str
    status: str
    type: str
    date_introduced: date


class UpdateLegislationDTO(BaseModel):
    title: str | None = None
    bill_number: str | None = None
    session_number: int | None = None
    sponsor_id: int | None = None
    sponsor_name: str | None = None
    summary: str | None = None
    full_text: str | None = None
    status: str | None = None
    type: str | None = None
    date_introduced: date | None = None


class CreateLegislationActionDTO(BaseModel):
    legislation_id: int
    action_date: date
    description: str
    action_type: str


class UpdateLegislationActionDTO(BaseModel):
    action_date: date | None = None
    description: str | None = None
    action_type: str | None = None
