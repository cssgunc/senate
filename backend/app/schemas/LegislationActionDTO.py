from datetime import date

from pydantic import BaseModel, ConfigDict


class LegislationActionDTO(BaseModel):
    id: int
    action_date: date
    description: str
    action_type: str

    model_config = ConfigDict(from_attributes=True)
