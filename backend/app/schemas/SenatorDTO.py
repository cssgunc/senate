from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .CommitteeAssignmentDTO import CommitteeAssignmentDTO


class SenatorDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    headshot_url: Optional[str] = None
    district_id: int
    is_active: bool
    session_number: int
    committees: List[CommitteeAssignmentDTO]

    model_config = ConfigDict(from_attributes=True)
