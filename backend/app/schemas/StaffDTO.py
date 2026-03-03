from typing import Optional

from pydantic import BaseModel, ConfigDict


class StaffDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: str
    email: str
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
