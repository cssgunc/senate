from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class CommitteeAssignmentDTO(BaseModel):
    committee_id: int
    committee_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)
