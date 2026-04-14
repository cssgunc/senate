"""Staff schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict, EmailStr


class StaffDTO(BaseModel):
    id: int
    first_name: str
    last_name: str
    title: str
    email: str
    photo_url: str | None

    model_config = ConfigDict(from_attributes=True)


class CreateStaffDTO(BaseModel):
    first_name: str
    last_name: str
    title: str
    email: EmailStr
    display_order: int


class UpdateStaffDTO(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    title: str | None = None
    email: EmailStr | None = None
    photo_url: str | None = None
    display_order: int | None = None
    is_active: bool | None = None
