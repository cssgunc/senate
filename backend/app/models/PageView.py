"""PageView model — server-side pageview analytics captured via Next.js proxy.

visitor_hash is a daily-rotating, non-reversible hash (never a raw IP or a
cookie), used only to approximate unique visitor counts.
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class PageView(Base):
    __tablename__ = "page_view"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String(500), nullable=False)
    referrer_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    visitor_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_page_view_created_at", "created_at"),
        Index("ix_page_view_path", "path"),
    )

    def __repr__(self) -> str:
        return f"<PageView id={self.id} path={self.path!r} created_at={self.created_at}>"
