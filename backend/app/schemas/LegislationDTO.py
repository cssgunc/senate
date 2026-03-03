from datetime import date
from typing import List

from pydantic import BaseModel, ConfigDict

from .LegislationActionDTO import LegislationActionDTO


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
    actions: List[LegislationActionDTO]

    model_config = ConfigDict(from_attributes=True)
