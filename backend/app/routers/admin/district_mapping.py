"""Admin district mapping CRUD routes.

GET    /api/admin/districts/{district_id}/mappings          — list mappings for a district
POST   /api/admin/districts/{district_id}/mappings          — create mapping for a district
DELETE /api/admin/districts/{district_id}/mappings/{map_id} — delete a mapping
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.District import District, DistrictMapping
from app.schemas.district import CreateDistrictMappingDTO, DistrictMappingDTO

router = APIRouter(
    prefix="/api/admin/districts",
    tags=["admin", "districts"],
)


@router.get("/{district_id}/mappings", response_model=list[DistrictMappingDTO])
def list_district_mappings(
    district_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return all mappings for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")

    mappings = db.query(DistrictMapping).filter(
        DistrictMapping.district_id == district_id
    ).all()
    return [DistrictMappingDTO.model_validate(m) for m in mappings]


@router.post(
    "/{district_id}/mappings",
    response_model=DistrictMappingDTO,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"description": "District not found"}},
)
def create_district_mapping(
    district_id: int,
    body: CreateDistrictMappingDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a mapping for a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")

    mapping = DistrictMapping(
        district_id=district_id,
        mapping_value=body.mapping_value,
    )
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return DistrictMappingDTO.model_validate(mapping)


@router.delete(
    "/{district_id}/mappings/{map_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "District or mapping not found"}},
)
def delete_district_mapping(
    district_id: int,
    map_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a mapping from a district."""
    district = db.query(District).filter(District.id == district_id).first()
    if district is None:
        raise HTTPException(status_code=404, detail="District not found")

    mapping = db.query(DistrictMapping).filter(
        DistrictMapping.id == map_id,
        DistrictMapping.district_id == district_id,
    ).first()
    if mapping is None:
        raise HTTPException(status_code=404, detail="Mapping not found")

    db.delete(mapping)
    db.commit()
    return None
