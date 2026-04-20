"""Admin news CRUD routes (TDD Section 4.5, ticket #62).

GET    /api/admin/news       — paginated list including drafts; optional is_published filter
POST   /api/admin/news       — create article; author_id set from JWT, not request body
PUT    /api/admin/news/{id}  — update article fields
DELETE /api/admin/news/{id}  — delete article; restricted to admin role (not staff)

All routes require authentication via get_current_user.
DELETE additionally requires require_role("admin").
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.Admin import Admin
from app.models.cms import News
from app.schemas.news import AdminNewsDTO, CreateNewsDTO, UpdateNewsDTO
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate
from app.utils.sanitization import sanitize_html

router = APIRouter(prefix="/api/admin/news", tags=["admin-news"])


def _news_to_dict(news: News) -> dict[str, Any]:
    """Map ORM row → dict compatible with AdminNewsDTO.

    NewsDTO (and its subclass AdminNewsDTO) expects the relationship field to
    be named ``admin``, but the ORM relationship is called ``author``.
    """
    return {
        "id": news.id,
        "title": news.title,
        "summary": news.summary,
        "body": sanitize_html(news.body),
        "image_url": news.image_url,
        "is_published": news.is_published,
        "date_published": news.date_published,
        "date_last_edited": news.date_last_edited,
        "admin": news.author,
    }


@router.get("", response_model=PaginatedResponse[AdminNewsDTO])
def list_admin_news(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    is_published: Optional[bool] = Query(default=None, description="Filter by published state"),
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a paginated list of all news articles (including drafts).

    Pass ``is_published=true`` or ``is_published=false`` to filter by state.
    """
    query = db.query(News).order_by(News.date_published.desc())
    if is_published is not None:
        query = query.filter(News.is_published == is_published)
    items, total = paginate(query, page=page, limit=limit)
    validated = [AdminNewsDTO.model_validate(_news_to_dict(n)) for n in items]
    return PaginatedResponse(items=validated, total=total, page=page, limit=limit)


@router.post("", response_model=AdminNewsDTO, status_code=201)
def create_news(
    body: CreateNewsDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new news article. author_id is set from the authenticated user."""
    payload = body.model_dump()
    payload["body"] = sanitize_html(payload["body"])

    article = News(**payload, author_id=current_user.id)
    db.add(article)
    db.commit()
    db.refresh(article)
    return AdminNewsDTO.model_validate(_news_to_dict(article))


@router.put("/{news_id}", response_model=AdminNewsDTO)
def update_news(
    news_id: int,
    body: UpdateNewsDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an existing news article."""
    article = db.query(News).filter(News.id == news_id).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    for field, value in body.model_dump().items():
        if field == "body":
            value = sanitize_html(value)
        setattr(article, field, value)
    db.commit()
    db.refresh(article)
    return AdminNewsDTO.model_validate(_news_to_dict(article))


@router.delete("/{news_id}", status_code=204)
def delete_news(
    news_id: int,
    current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a news article. Requires admin role (not staff)."""
    article = db.query(News).filter(News.id == news_id).first()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    db.delete(article)
    db.commit()
