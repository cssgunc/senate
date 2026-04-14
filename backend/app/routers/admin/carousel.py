"""Admin carousel slide CRUD routes.

POST /api/admin/carousel          — create slide
PUT  /api/admin/carousel/reorder  — batch reorder slides by ordered slide_ids list
PUT  /api/admin/carousel/{id}     — update slide fields
DELETE /api/admin/carousel/{id}   — delete slide
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.CarouselSlide import CarouselSlide
from app.schemas.carousel import (
    CarouselSlideDTO,
    CreateCarouselSlideDTO,
    ReorderCarouselDTO,
    UpdateCarouselSlideDTO,
)

router = APIRouter(
    prefix="/api/admin/carousel",
    tags=["admin", "carousel"],
)


@router.post("", response_model=CarouselSlideDTO, status_code=status.HTTP_201_CREATED)
def create_admin_slide(
    body: CreateCarouselSlideDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a carousel slide."""
    slide = CarouselSlide(**body.model_dump())
    db.add(slide)
    db.commit()
    db.refresh(slide)
    return CarouselSlideDTO.model_validate(slide)


@router.put(
    "/reorder",
    response_model=list[CarouselSlideDTO],
    responses={400: {"description": "slide_ids do not match existing slides"}},
)
def reorder_admin_slides(
    body: ReorderCarouselDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Batch-reorder carousel slides. Accepts an ordered list of slide IDs and
    updates display_order to match the given ordering (1-based)."""
    slides = {s.id: s for s in db.query(CarouselSlide).all()}

    if set(body.slide_ids) != set(slides.keys()):
        raise HTTPException(
            status_code=400,
            detail="slide_ids must contain exactly the IDs of all existing slides",
        )

    for order, slide_id in enumerate(body.slide_ids, start=1):
        slides[slide_id].display_order = order

    db.commit()

    ordered = sorted(slides.values(), key=lambda s: s.display_order)
    return [CarouselSlideDTO.model_validate(s) for s in ordered]


@router.put(
    "/{slide_id}",
    response_model=CarouselSlideDTO,
    responses={404: {"description": "Slide not found"}},
)
def update_admin_slide(
    slide_id: int,
    body: UpdateCarouselSlideDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update carousel slide fields. Unset fields remain unchanged."""
    slide = db.query(CarouselSlide).filter(CarouselSlide.id == slide_id).first()
    if slide is None:
        raise HTTPException(status_code=404, detail="Slide not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(slide, field, value)

    db.commit()
    db.refresh(slide)
    return CarouselSlideDTO.model_validate(slide)


@router.delete(
    "/{slide_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Slide not found"}},
)
def delete_admin_slide(
    slide_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a carousel slide."""
    slide = db.query(CarouselSlide).filter(CarouselSlide.id == slide_id).first()
    if slide is None:
        raise HTTPException(status_code=404, detail="Slide not found")

    db.delete(slide)
    db.commit()
    return None
