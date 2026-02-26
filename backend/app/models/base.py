"""Shared SQLAlchemy Base for models.

Keep a single Base instance across the app so metadata is centralized.
"""

from app.database import Base as _Base

Base = _Base

__all__ = ["Base"]
