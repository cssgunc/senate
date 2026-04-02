"""Senators public API routes (TDD Section 4.5.2).

GET /api/senators         — filterable roster (search, district_id, committee, session)
GET /api/senators/{id}    — single senator with committee assignments

Schemas (SenatorDTO, CommitteeAssignmentDTO) are provided by PR #37 (ticket #10).
The try/except guard allows this module to be imported and tested before that PR merges.
"""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, true
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import Committee, CommitteeMembership
from app.models.Senator import Senator

try:
    from app.schemas.senator import CommitteeAssignmentDTO as _CommitteeAssignmentDTO  # noqa: F401
    from app.schemas.senator import SenatorDTO as _SenatorDTO  # noqa: F401

    _SENATOR_DTO_AVAILABLE = True
except ImportError:  # pragma: no cover — removed once PR #37 merges
    _SENATOR_DTO_AVAILABLE = False

router = APIRouter(prefix="/api/senators", tags=["senators"])


def _senator_to_dict(senator: Senator, db: Session) -> dict[str, Any]:
    """Convert a Senator ORM row to a dict compatible with PR #37's SenatorDTO.

    Key remappings vs the model:
    - ``district``  (model column)  → ``district_id``  (DTO field in PR #37)
    - ``committee_memberships``  (relationship)  → ``committees``  (DTO field in PR #37)

    Memberships are queried explicitly to avoid SQLAlchemy inference issues with
    the untyped ``Mapped[list]`` annotation on ``Senator.committee_memberships``.
    """
    memberships = (
        db.query(CommitteeMembership).filter(CommitteeMembership.senator_id == senator.id).all()
    )
    committee_ids = [m.committee_id for m in memberships]
    committees_by_id = (
        {c.id: c.name for c in db.query(Committee).filter(Committee.id.in_(committee_ids)).all()}
        if committee_ids
        else {}
    )

    committees = [
        {
            "committee_id": m.committee_id,
            "committee_name": committees_by_id.get(m.committee_id, ""),
            "role": m.role,
        }
        for m in memberships
    ]
    return {
        "id": senator.id,
        "first_name": senator.first_name,
        "last_name": senator.last_name,
        "email": senator.email,
        "headshot_url": senator.headshot_url,
        "district_id": senator.district,  # model col = "district"; DTO = "district_id"
        "is_active": senator.is_active,
        "session_number": senator.session_number,
        "committees": committees,
    }


def _base_query(db: Session):
    """Base query for senators."""
    return db.query(Senator)


def _current_session(db: Session) -> int:
    """Return the highest session_number present in the senator table."""
    result = db.query(func.max(Senator.session_number)).scalar()
    return result or 1


@router.get("")
def list_senators(
    search: Optional[str] = Query(default=None, description="Partial name search (first or last)"),
    district_id: Optional[int] = Query(default=None, description="Filter by district ID"),
    committee: Optional[int] = Query(default=None, description="Filter by committee ID"),
    session: Optional[int] = Query(default=None, description="Session number; defaults to current"),
    db: Session = Depends(get_db),
):
    """Return a filterable list of senators.

    Defaults to active senators in the current (highest) session.
    ``search`` performs a case-insensitive partial match on first_name + last_name.
    ``committee`` filters senators who are members of that committee via CommitteeMembership.
    """
    target_session = session if session is not None else _current_session(db)

    query = _base_query(db).filter(
        Senator.is_active == true(),
        Senator.session_number == target_session,
    )

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                func.lower(Senator.first_name).like(func.lower(pattern)),
                func.lower(Senator.last_name).like(func.lower(pattern)),
            )
        )

    if district_id is not None:
        query = query.filter(Senator.district == district_id)

    if committee is not None:
        query = query.join(
            CommitteeMembership,
            CommitteeMembership.senator_id == Senator.id,
        ).filter(CommitteeMembership.committee_id == committee)

    senators_orm = query.all()
    dicts: list[Any] = [_senator_to_dict(s, db) for s in senators_orm]

    if _SENATOR_DTO_AVAILABLE:
        from app.schemas.senator import SenatorDTO

        return [SenatorDTO.model_validate(d) for d in dicts]
    return dicts


@router.get("/{senator_id}")
def get_senator(senator_id: int, db: Session = Depends(get_db)):
    """Return a single senator with committee assignments, or 404."""
    senator = _base_query(db).filter(Senator.id == senator_id).first()
    if senator is None:
        raise HTTPException(status_code=404, detail="Senator not found")

    data = _senator_to_dict(senator, db)
    if _SENATOR_DTO_AVAILABLE:
        from app.schemas.senator import SenatorDTO

        return SenatorDTO.model_validate(data)
    return data
