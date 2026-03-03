"""Reusable pagination utility (TDD Section 4.5.2).

Usage::

    from app.utils.pagination import paginate

    items, total = paginate(query, page=1, limit=20)
"""

from typing import TypeVar

from sqlalchemy.orm import Query

T = TypeVar("T")


def paginate(query: "Query[T]", page: int, limit: int) -> tuple[list[T], int]:
    """Return a page of results and the total un-paginated count.

    Args:
        query:  A SQLAlchemy ``Query`` object (filters/joins already applied).
        page:   1-based page number.
        limit:  Maximum number of items to return.

    Returns:
        A ``(items, total)`` tuple where ``items`` is the current page slice
        and ``total`` is the count of all rows matching the query.
    """
    total: int = query.count()
    items: list[T] = query.offset((page - 1) * limit).limit(limit).all()
    return items, total
