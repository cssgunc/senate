from typing import Optional

from pydantic import BaseModel, ConfigDict


class LeadershipDTO(BaseModel):
    id: int
    title: str
    first_name: str
    last_name: str
    email: str
    photo_url: Optional[str] = None
    session_number: int
    is_current: bool

    model_config = ConfigDict(from_attributes=True)
