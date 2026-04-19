"""Senator schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict, EmailStr


class CommitteeAssignmentDTO(BaseModel):
    committee_id: int
    committee_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class SenatorDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    headshot_url: str | None
    district_id: int
    is_active: bool
    session_number: int
    committees: list[CommitteeAssignmentDTO]

    model_config = ConfigDict(from_attributes=True)


class CreateSenatorDTO(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    district_id: int
    session_number: int


class UpdateSenatorDTO(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    district_id: int | None = None
    is_active: bool | None = None
    session_number: int | None = None
