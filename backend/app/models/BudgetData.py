from .base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, String, DateTime, DECIMAL, ForeignKey, func

class BudgetData(Base):
    __tablename__ = "budget_data"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    category: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    parent_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("budget_data.id"), nullable=True
    )

    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_by: Mapped[int] = mapped_column(ForeignKey("admin.id"), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
