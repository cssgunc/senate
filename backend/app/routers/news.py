"""News public API routes (TDD Section 4.5.2).

GET /api/news         — paginated list, published only, most recent first
GET /api/news/{id}    — single article, 404 if not found or unpublished

Schemas (NewsDTO) are provided by PR #37 (ticket #10).  The try/except guard
allows this module to be imported and fully tested before PR #37 merges;
DTO validation is applied automatically once the schemas are available.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import true
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import News
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate

try:
    from app.schemas.news import NewsDTO as _NewsDTO

    _NEWS_DTO_AVAILABLE = True
except ImportError:  # pragma: no cover — removed once PR #37 merges
    _NewsDTO = None  # type: ignore[assignment,misc]
    _NEWS_DTO_AVAILABLE = False

router = APIRouter(prefix="/api/news", tags=["news"])


def _news_to_dict(news: News) -> dict[str, Any]:
    """Convert a News ORM row to a dict compatible with NewsDTO.

    NewsDTO expects a field called ``admin`` (not ``author``) so we
    remap the relationship here rather than in the model.
    """
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "body": news.body,
        "image_url": news.image_url,
        "date_published": news.date_published,
        "date_last_edited": news.date_last_edited,
        "admin": news.author,
    }


@router.get("")
def list_news(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of published news articles, most recent first."""
    query = db.query(News).filter(News.is_published == true()).order_by(News.date_published.desc())
    items, total = paginate(query, page=page, limit=limit)
    news_dicts = [_news_to_dict(n) for n in items]

    if _NEWS_DTO_AVAILABLE:
        from app.schemas.news import NewsDTO

        validated: list[Any] = [NewsDTO.model_validate(d) for d in news_dicts]
    else:
        validated = news_dicts

    return PaginatedResponse(items=validated, total=total, page=page, limit=limit)


@router.get("/{news_id}")
def get_news(news_id: int, db: Session = Depends(get_db)):
    """Return a single published news article by ID, or 404."""
    news = db.query(News).filter(News.id == news_id, News.is_published == true()).first()
    if news is None:
        raise HTTPException(status_code=404, detail="Article not found")

    data = _news_to_dict(news)
    if _NEWS_DTO_AVAILABLE:
        from app.schemas.news import NewsDTO

        return NewsDTO.model_validate(data)
    return data
