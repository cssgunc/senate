"""Admin district CRUD routes.

GET    /api/admin/districts       — list all districts
POST   /api/admin/districts       — create district
PUT    /api/admin/districts/{id}  — update district fields
DELETE /api/admin/districts/{id}  — delete district
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.District import District
from app.schemas.district import AdminDistrictDTO, CreateDistrictDTO, UpdateDistrictDTO

router = APIRouter(
    prefix="/api/admin/districts",
    tags=["admin", "districts"],
)


@router.get("", response_model=list[AdminDistrictDTO])
def list_admin_districts(
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all districts."""
    districts = db.query(District).order_by(District.district_name).all()
    return [AdminDistrictDTO.model_validate(d) for d in districts]


@router.post("", response_model=AdminDistrictDTO, status_code=status.HTTP_201_CREATED)
def create_admin_district(
    body: CreateDistrictDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a district."""
    district = District(**body.model_dump())
    db.add(district)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to create district due to invalid data")
    db.refresh(district)
    return AdminDistrictDTO.model_validate(district)


@router.put(
    "/{district_id}",
    response_model=AdminDistrictDTO,
    responses={404: {"description": "District not found"}},
)
def update_admin_district(
    district_id: int,
    body: UpdateDistrictDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update district fields. Unset fields remain unchanged."""
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(district, field, value)

    db.commit()
    db.refresh(district)
    return AdminDistrictDTO.model_validate(district)


@router.delete(
    "/{district_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "District not found"},
        409: {"description": "District has linked senators"},
    },
)
def delete_admin_district(
    district_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a district. Blocked if senators are still assigned to it."""
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")

    try:
        db.delete(district)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="District has linked senators; reassign or delete them first",
        )
    return None
