"""Districts public API routes (TDD Section 4.5.2).

GET /api/districts         — all districts with nested active senators
GET /api/districts/lookup  — case-insensitive partial match on DistrictMapping.mapping_value
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import Committee, CommitteeMembership
from app.models.District import District, DistrictMapping
from app.models.Senator import Senator
from app.schemas.district import DistrictDTO

router = APIRouter(prefix="/api/districts", tags=["districts"])


def _senator_to_dict(senator: Senator, db: Session) -> dict[str, Any]:
    memberships = (
        db.query(CommitteeMembership).filter(CommitteeMembership.senator_id == senator.id).all()
    )
    committee_ids = [m.committee_id for m in memberships]
    committees_by_id = (
        {c.id: c.name for c in db.query(Committee).filter(Committee.id.in_(committee_ids)).all()}
        if committee_ids
        else {}
    )
    return {
        "id": senator.id,
        "first_name": senator.first_name,
        "last_name": senator.last_name,
        "email": senator.email,
        "headshot_url": senator.headshot_url,
        "district_id": senator.district,
        "is_active": senator.is_active,
        "session_number": senator.session_number,
        "committees": [
            {
                "committee_id": m.committee_id,
                "committee_name": committees_by_id.get(m.committee_id, ""),
                "role": m.role,
            }
            for m in memberships
        ],
    }


def _district_to_dict(district: District, db: Session) -> dict[str, Any]:
    senators = (
        db.query(Senator).filter(Senator.district == district.id, Senator.is_active.is_(True)).all()
    )
    return {
        "id": district.id,
        "district_name": district.district_name,
        "description": district.description,
        "senator": [_senator_to_dict(s, db) for s in senators],
    }


@router.get("/lookup", response_model=list[DistrictDTO])
def lookup_district(
    query: str = Query(..., description="Case-insensitive partial match on mapping value"),
    db: Session = Depends(get_db),
):
    pattern = f"%{query.lower()}%"
    mappings = (
        db.query(DistrictMapping)
        .filter(func.lower(DistrictMapping.mapping_value).like(pattern))
        .all()
    )
    district_ids = list({m.district_id for m in mappings})
    if not district_ids:
        return []
    districts = db.query(District).filter(District.id.in_(district_ids)).all()
    return [DistrictDTO.model_validate(_district_to_dict(d, db)) for d in districts]


@router.get("", response_model=list[DistrictDTO])
def list_districts(db: Session = Depends(get_db)):
    districts = db.query(District).all()
    return [DistrictDTO.model_validate(_district_to_dict(d, db)) for d in districts]
