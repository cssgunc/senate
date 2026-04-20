"""Carousel slide schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict


class CarouselSlideDTO(BaseModel):
    id: int
    image_url: str
    overlay_text: str | None
    link_url: str | None
    display_order: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class CreateCarouselSlideDTO(BaseModel):
    image_url: str
    overlay_text: str
    link_url: str
    display_order: int
    is_active: bool


class UpdateCarouselSlideDTO(BaseModel):
    image_url: str | None = None
    overlay_text: str | None = None
    link_url: str | None = None
    display_order: int | None = None
    is_active: bool | None = None


class ReorderCarouselDTO(BaseModel):
    slide_ids: list[int]
