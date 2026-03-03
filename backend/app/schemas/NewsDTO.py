from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field, field_serializer

from .AccountDTO import AccountDTO


class NewsDTO(BaseModel):
    id: int
    title: str
    summary: str
    body: str
    image_url: Optional[str] = None
    date_published: datetime
    date_last_edited: datetime

    author: Optional[AccountDTO] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("author", when_used="json")
    def serialize_author(self, value: Optional[AccountDTO]) -> None:
        # Exclude author from JSON serialization — only author_name is public per spec
        return None

    @computed_field
    @property
    def author_name(self) -> str:
        if self.author:
            return f"{self.author.first_name} {self.author.last_name}"
        return "Unknown"
