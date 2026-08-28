"""Sections and AdminSections models."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Sections(Base):
    __tablename__ = "sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)


class AdminSections(Base):
    __tablename__ = "admin_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("sections.id"), nullable=False)
    # Membership row is meaningless without the admin — delete it alongside them.
    admin_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("admin.id", ondelete="CASCADE"), nullable=False
    )
