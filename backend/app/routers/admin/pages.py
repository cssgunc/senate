"""Admin static pages routes.

GET /api/admin/pages        — list all static pages
PUT /api/admin/pages/{slug} — update page content; last_edited_by set from JWT
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.cms import StaticPageContent
from app.schemas.static_page import StaticPageDTO, UpdateStaticPageDTO
from app.utils.sanitization import sanitize_html

router = APIRouter(
    prefix="/api/admin/pages",
    tags=["admin", "pages"],
)


@router.get("", response_model=list[StaticPageDTO])
def list_admin_pages(
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all static pages."""
    pages = db.query(StaticPageContent).order_by(StaticPageContent.page_slug).all()
    return [StaticPageDTO.model_validate(p) for p in pages]


@router.put(
    "/{slug}",
    response_model=StaticPageDTO,
    responses={404: {"description": "Page not found"}},
)
def update_admin_page(
    slug: str,
    body: UpdateStaticPageDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update static page content. Pages are pre-seeded; only editing is allowed."""
    page = db.query(StaticPageContent).filter(StaticPageContent.page_slug == slug).first()
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")

    page.title = body.title
    page.body = sanitize_html(body.body)
    page.last_edited_by = current_user.id

    db.commit()
    db.refresh(page)
    return StaticPageDTO.model_validate(page)
