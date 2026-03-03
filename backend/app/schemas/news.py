"""News schemas — input and output DTOs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NewsDTO(BaseModel):
    id: int
    title: str
    summary: str
    body: str
    image_url: str | None
    author_name: str
    date_published: datetime
    date_last_edited: datetime

    model_config = ConfigDict(from_attributes=True)


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
