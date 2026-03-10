"""Senator model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import CHAR, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Senator(Base):
    __tablename__ = "senator"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    headshot_url: Mapped[Optional[str]] = mapped_column(CHAR(500), nullable=True)
    district: Mapped[int] = mapped_column(Integer, ForeignKey("district.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    session_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships (referenced by cms.py)
    committee_memberships: Mapped[list] = relationship(
        "CommitteeMembership", back_populates="senator"
    )

    def __repr__(self) -> str:
        return f"<Senator id={self.id} name={self.first_name!r} {self.last_name!r} active={self.is_active}>"
