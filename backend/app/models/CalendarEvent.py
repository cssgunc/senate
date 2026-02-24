from .base import Base
from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column



class CalendarEvent(Base):
    __tablename__ = "calendar_event"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("admin.id"), nullable=False)
