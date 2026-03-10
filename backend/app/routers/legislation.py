"""Legislation public API routes (ticket #35).

GET /api/legislation         — paginated list, filterable
GET /api/legislation/recent  — most recent N items, optionally filtered by type
GET /api/legislation/{id}    — single item with ordered actions list

NOTE: /recent MUST be registered before /{id} to avoid route conflict.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.Legislation import Legislation
from app.models.LegislationAction import LegislationAction
from app.schemas.legislation import LegislationActionDTO, LegislationDTO
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/legislation", tags=["legislation"])


def _current_session(db: Session) -> int:
    result = db.query(func.max(Legislation.session_number)).scalar()
    return result or 1


def _legislation_to_dict(leg: Legislation, db: Session) -> dict:
    actions = (
        db.query(LegislationAction)
        .filter(LegislationAction.legislation_id == leg.id)
        .order_by(LegislationAction.display_order)
        .all()
    )
    return {
        "id": leg.id,
        "title": leg.title,
        "bill_number": leg.bill_number,
        "session_number": leg.session_number,
        "sponsor_name": leg.sponsor_name,
        "summary": leg.summary,
        "full_text": leg.full_text,
        "status": leg.status,
        "type": leg.type,
        "date_introduced": leg.date_introduced,
        "date_last_action": leg.date_last_action,
        "actions": [LegislationActionDTO.model_validate(a, from_attributes=True) for a in actions],
    }


# /recent BEFORE /{id}
@router.get("/recent")
def get_recent_legislation(
    limit: int = Query(default=10, ge=1, le=100, description="Max items to return"),
    type: Optional[str] = Query(default=None, description="Filter by legislation type"),
    db: Session = Depends(get_db),
):
    """Return the most recently introduced legislation, optionally filtered by type."""
    query = db.query(Legislation).order_by(Legislation.date_introduced.desc())
    if type is not None:
        query = query.filter(Legislation.type == type)
    items = query.limit(limit).all()
    return [LegislationDTO.model_validate(_legislation_to_dict(leg, db)) for leg in items]


@router.get("")
def list_legislation(
    search: Optional[str] = Query(
        default=None, description="Keyword search across title, bill_number, summary, full_text"
    ),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    type: Optional[str] = Query(default=None, description="Filter by type"),
    session: Optional[int] = Query(default=None, description="Session number; defaults to current"),
    sponsor: Optional[str] = Query(default=None, description="Partial match on sponsor name"),
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Return a paginated, filterable list of legislation for a given session."""
    target_session = session if session is not None else _current_session(db)
    query = db.query(Legislation).filter(Legislation.session_number == target_session)

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                Legislation.title.ilike(pattern),
                Legislation.bill_number.ilike(pattern),
                Legislation.summary.ilike(pattern),
                Legislation.full_text.ilike(pattern),
            )
        )

    if status:
        query = query.filter(Legislation.status == status)

    if type:
        query = query.filter(Legislation.type == type)

    if sponsor:
        query = query.filter(Legislation.sponsor_name.ilike(f"%{sponsor}%"))

    query = query.order_by(Legislation.date_introduced.desc())
    items, total = paginate(query, page=page, limit=limit)
    validated = [LegislationDTO.model_validate(_legislation_to_dict(leg, db)) for leg in items]
    return PaginatedResponse(items=validated, total=total, page=page, limit=limit)


@router.get("/{legislation_id}")
def get_legislation(legislation_id: int, db: Session = Depends(get_db)):
    """Return a single legislation item with its ordered actions list, or 404."""
    leg = db.query(Legislation).filter(Legislation.id == legislation_id).first()
    if leg is None:
        raise HTTPException(status_code=404, detail="Legislation not found")
    return LegislationDTO.model_validate(_legislation_to_dict(leg, db))
