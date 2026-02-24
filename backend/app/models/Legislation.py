from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

legislation_status_values = ["Introduced", "In Committee", "Passed", "Failed"]

class Legislation(Base):
    __tablename__ = "legislation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    bill_number: Mapped[str] = mapped_column(String(50), nullable=False)
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sponsor_id: Mapped[int | None] = mapped_column(
        ForeignKey("senator.id"),
        nullable=True
    )
    sponsor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(*legislation_status_values),
        nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    date_introduced: Mapped[date] = mapped_column(Date, nullable=False)
    date_last_action: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
