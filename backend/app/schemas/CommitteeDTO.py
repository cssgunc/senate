from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict

from .SenatorDTO import SenatorDTO


class CommitteeDTO(BaseModel):
    id: int
    name: str
    description: str
    chair_name: str
    chair_email: str
    members: List[SenatorDTO]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
