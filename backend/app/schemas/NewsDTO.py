from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field


class NewsDTO(BaseModel):
    id: int
    title: str
    summary: str
    body: str
    image_url: Optional[str] = None
    date_published: datetime
    date_last_edited: datetime

    admin: Optional[object] = None

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def author_name(self) -> str:
        if self.admin:
            return f"{self.admin.first_name} {self.admin.last_name}"
        return "Unknown"
