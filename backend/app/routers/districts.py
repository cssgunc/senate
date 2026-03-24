"""Districts public API routes (TDD Section 4.5.2).

GET /api/districts         — all districts with nested active senators
GET /api/districts/lookup  — case-insensitive partial match on DistrictMapping.mapping_value
"""

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, true
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import Committee, CommitteeMembership
from app.models.District import District, DistrictMapping
from app.models.Senator import Senator
from app.schemas.district import DistrictDTO

router = APIRouter(prefix="/api/districts", tags=["districts"])


def _senator_to_dict(
    senator: Senator,
    memberships: list[CommitteeMembership],
    committees_by_id: dict[int, str],
) -> dict[str, Any]:
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


def _districts_to_dto(districts: list[District], db: Session) -> list[DistrictDTO]:
    if not districts:
        return []

    district_ids = [district.id for district in districts]
    senators = (
        db.query(Senator)
        .filter(Senator.district.in_(district_ids), Senator.is_active == true())
        .all()
    )

    senators_by_district: dict[int, list[Senator]] = {district.id: [] for district in districts}
    for senator in senators:
        senators_by_district.setdefault(senator.district, []).append(senator)

    senator_ids = [senator.id for senator in senators]
    memberships: list[CommitteeMembership] = []
    if senator_ids:
        memberships = (
            db.query(CommitteeMembership)
            .filter(CommitteeMembership.senator_id.in_(senator_ids))
            .all()
        )

    memberships_by_senator: dict[int, list[CommitteeMembership]] = {senator_id: [] for senator_id in senator_ids}
    for membership in memberships:
        memberships_by_senator.setdefault(membership.senator_id, []).append(membership)

    committee_ids = list({membership.committee_id for membership in memberships})
    committees_by_id: dict[int, str] = {}
    if committee_ids:
        committees_by_id = {
            committee.id: committee.name
            for committee in db.query(Committee).filter(Committee.id.in_(committee_ids)).all()
        }

    return [
        DistrictDTO.model_validate(
            {
                "id": district.id,
                "district_name": district.district_name,
                "description": district.description,
                "senator": [
                    _senator_to_dict(
                        senator,
                        memberships_by_senator.get(senator.id, []),
                        committees_by_id,
                    )
                    for senator in senators_by_district.get(district.id, [])
                ],
            }
        )
        for district in districts
    ]


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
    return _districts_to_dto(districts, db)


@router.get("", response_model=list[DistrictDTO])
def list_districts(db: Session = Depends(get_db)):
    districts = db.query(District).all()
    return _districts_to_dto(districts, db)
