"""Calendar event schemas — input and output DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator


class CalendarEventDTO(BaseModel):
    id: int
    title: str
    description: str | None
    start_datetime: datetime
    end_datetime: datetime
    location: str | None
    event_type: str

    model_config = ConfigDict(from_attributes=True)


class CreateCalendarEventDTO(BaseModel):
    title: str
    description: str | None
    start_datetime: datetime
    end_datetime: datetime
    location: str | None
    event_type: str

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "CreateCalendarEventDTO":
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self
