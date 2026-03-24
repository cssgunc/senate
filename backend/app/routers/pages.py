"""Static pages public API routes (TDD Section 4.5.2).

GET /api/pages/{slug} — static page content by slug, 404 if not found
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import StaticPageContent
from app.schemas.static_page import StaticPageDTO

router = APIRouter(prefix="/api/pages", tags=["pages"])


@router.get("/{slug}", response_model=StaticPageDTO)
def get_page(slug: str, db: Session = Depends(get_db)):
    page = db.query(StaticPageContent).filter(StaticPageContent.page_slug == slug).first()
    if page is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return StaticPageDTO.model_validate(page)
