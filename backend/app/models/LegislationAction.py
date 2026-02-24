from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class LegislationAction(Base):
    __tablename__ = "legislation_action"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    legislation_id: Mapped[int] = mapped_column(
    ForeignKey("legislation.id"),
    nullable=False
    )
    action_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
