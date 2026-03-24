"""Carousel public API routes (TDD Section 4.5.2).

GET /api/carousel — active slides only, ordered by display_order
"""

from fastapi import APIRouter, Depends
from sqlalchemy import true
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.CarouselSlide import CarouselSlide
from app.schemas.carousel import CarouselSlideDTO

router = APIRouter(prefix="/api/carousel", tags=["carousel"])


@router.get("", response_model=list[CarouselSlideDTO])
def list_carousel(db: Session = Depends(get_db)):
    slides = (
        db.query(CarouselSlide)
        .filter(CarouselSlide.is_active == true())
        .order_by(CarouselSlide.display_order)
        .all()
    )
    return [CarouselSlideDTO.model_validate(s) for s in slides]
