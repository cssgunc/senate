"""Generic pagination response envelope.

Kept separate from the DTO files so it can be imported directly
(``from app.schemas.pagination import PaginatedResponse``) without conflicting
with the ``__init__.py`` additions made by the schemas PR.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response envelope.

    ``items``  — the page of results.
    ``total``  — total number of records matching the query (before pagination).
    ``page``   — current 1-based page number.
    ``limit``  — maximum items per page.
    """

    items: list[T]
    total: int
    page: int
    limit: int
