"""UptimeCheck model — periodic health-probe results.

Recorded by the senate-uptime-probe CronJob (deploy/cloudapps/template.yaml),
which hits the backend and frontend over cluster-internal Service DNS every
couple of minutes and posts each result here through the same shared-secret
ingest pattern as PageView.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class UptimeCheck(Base):
    __tablename__ = "uptime_check"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(String(32), nullable=False)
    is_up: Mapped[bool] = mapped_column(Boolean, nullable=False)
    latency_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    error: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_uptime_check_checked_at", "checked_at"),
        # Matches the summary/incident queries' per-target range scans.
        Index("ix_uptime_check_target_checked_at", "target", "checked_at"),
    )

    def __repr__(self) -> str:
        return f"<UptimeCheck id={self.id} target={self.target!r} is_up={self.is_up} checked_at={self.checked_at}>"
