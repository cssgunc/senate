"""Committee schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.senator import SenatorDTO


class CommitteeDTO(BaseModel):
    id: int
    name: str
    description: str
    chair_name: str
    chair_email: str
    members: list[SenatorDTO]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CreateCommitteeDTO(BaseModel):
    name: str
    description: str
    chair_senator_id: int | None
    chair_name: str
    chair_email: EmailStr


class AssignCommitteeMemberDTO(BaseModel):
    senator_id: int
    role: str
