from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CalendarEventDTO(BaseModel):
    id: int
    title: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    location: str | None = None
    event_type: str

    model_config = ConfigDict(from_attributes=True)
