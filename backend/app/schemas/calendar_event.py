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


class AdminCalendarEventDTO(BaseModel):
    id: int
    title: str
    description: str | None
    start_datetime: datetime
    end_datetime: datetime
    location: str | None
    event_type: str
    is_published: bool

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


class CreateAdminCalendarEventDTO(BaseModel):
    title: str
    description: str | None = None
    start_datetime: datetime
    end_datetime: datetime
    location: str | None = None
    event_type: str
    is_published: bool = False

    @model_validator(mode="after")
    def end_must_be_after_start(self) -> "CreateAdminCalendarEventDTO":
        if self.end_datetime <= self.start_datetime:
            raise ValueError("end_datetime must be after start_datetime")
        return self


class UpdateCalendarEventDTO(BaseModel):
    title: str | None = None
    description: str | None = None
    start_datetime: datetime | None = None
    end_datetime: datetime | None = None
    location: str | None = None
    event_type: str | None = None
    is_published: bool | None = None
