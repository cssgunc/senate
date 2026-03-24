from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StaticPageDTO(BaseModel):
    id: int
    page_slug: str
    title: str
    body: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
