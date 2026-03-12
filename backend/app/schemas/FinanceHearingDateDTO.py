from datetime import date, time
from typing import Optional

from pydantic import BaseModel, ConfigDict


class FinanceHearingDateDTO(BaseModel):
    id: int
    hearing_date: date
    hearing_time: time
    location: Optional[str] = None
    description: Optional[str] = None
    is_full: bool

    model_config = ConfigDict(from_attributes=True)
