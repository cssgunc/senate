from .base import Base
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey, func


class CarouselSlide(Base):
    __tablename__ = "carousel_slide"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    overlay_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    link_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
