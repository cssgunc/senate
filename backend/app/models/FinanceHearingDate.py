from datetime import date, time

from sqlalchemy import Boolean, Date, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

# effectively a singleton row

class FinanceHearingDate(Base):
    __tablename__ = "finance_hearing_date"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hearing_date: Mapped[date] = mapped_column(Date, nullable=False)
    hearing_time: Mapped[time] = mapped_column(Time, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_full: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
