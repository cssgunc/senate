"""News schemas — input and output DTOs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field

from .account import AccountDTO


class NewsDTO(BaseModel):
    id: int
    title: str
    summary: str
    body: str
    image_url: str | None
    date_published: datetime
    date_last_edited: datetime
    admin: Optional[AccountDTO] = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def author_name(self) -> str:
        if self.admin:
            return f"{self.admin.first_name} {self.admin.last_name}"
        return "Unknown"


class CreateNewsDTO(BaseModel):
    title: str
    body: str
    summary: str
    image_url: str | None
    is_published: bool


class UpdateNewsDTO(BaseModel):
    title: str
    body: str
    summary: str
    image_url: str | None
    is_published: bool


class AdminNewsDTO(NewsDTO):
    """NewsDTO extended with admin-only fields (e.g. draft status)."""

    is_published: bool
