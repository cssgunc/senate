"""Leadership schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict, EmailStr


class LeadershipDTO(BaseModel):
    id: int
    senator_id: int | None
    title: str
    first_name: str
    last_name: str
    email: str
    photo_url: str | None
    session_number: int
    is_current: bool

    model_config = ConfigDict(from_attributes=True)


class CreateLeadershipDTO(BaseModel):
    senator_id: int | None = None
    title: str
    first_name: str
    last_name: str
    email: EmailStr
    headshot_url: str | None = None
    is_active: bool = True
    session_number: int


class UpdateLeadershipDTO(BaseModel):
    senator_id: int | None = None
    title: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    headshot_url: str | None = None
    is_active: bool | None = None
    session_number: int | None = None
