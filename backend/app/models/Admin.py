"""Admin model for staff/admin accounts."""

from datetime import datetime

from sqlalchemy import CHAR, CheckConstraint, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from .base import Base


class Admin(Base):
    __tablename__ = "admin"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    pid: Mapped[str] = mapped_column(CHAR(9), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # "admin" or "staff"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint(
            "pid LIKE '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]'",
            name="ck_admin_pid_format",
        ),
    )

    # Relationships (referenced by cms.py)
    news_articles: Mapped[list] = relationship("News", back_populates="author")
    edited_pages: Mapped[list] = relationship("StaticPageContent", back_populates="editor")
    config_updates: Mapped[list] = relationship("AppConfig", back_populates="updater")

    def __repr__(self) -> str:
        return f"<Admin id={self.id} email={self.email!r} role={self.role!r}>"
