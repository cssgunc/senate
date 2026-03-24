from pydantic import BaseModel, ConfigDict


class CarouselSlideDTO(BaseModel):
    id: int
    image_url: str
    overlay_text: str
    link_url: str
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

