"""Legislation schemas — input and output DTOs."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class LegislationActionDTO(BaseModel):
    id: int
    action_date: date
    description: str
    action_type: str

    model_config = ConfigDict(from_attributes=True)


class LegislationDTO(BaseModel):
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
    actions: list[LegislationActionDTO]

    model_config = ConfigDict(from_attributes=True)


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


class CreateLegislationActionDTO(BaseModel):
    legislation_id: int
    action_date: date
    description: str
    action_type: str
