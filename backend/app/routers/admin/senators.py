"""Admin senator CRUD routes.

GET    /api/admin/senators       — paginated list; optional is_active/session filters
POST   /api/admin/senators       — create senator
PUT    /api/admin/senators/{id}  — update senator fields
DELETE /api/admin/senators/{id}  — delete senator (admin role required)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models import Leadership
from app.models.Admin import Admin
from app.models.cms import Committee, CommitteeMembership
from app.models.Senator import Senator
from app.schemas.pagination import PaginatedResponse
from app.schemas.senator import CreateSenatorDTO, SenatorDTO, UpdateSenatorDTO
from app.utils.pagination import paginate

router = APIRouter(
    prefix="/api/admin/senators",
    tags=["admin", "senators"],
)


def _serialize_senator(senator: Senator, db: Session) -> dict[str, Any]:
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
        "district_id": senator.district,
        "is_active": senator.is_active,
        "session_number": senator.session_number,
        "committees": committees,
    }


@router.get("", response_model=PaginatedResponse[SenatorDTO])
def list_admin_senators(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    is_active: bool | None = Query(default=None, description="Filter by active state"),
    session: int | None = Query(default=None, description="Filter by session number"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a paginated list of senators for admin workflows."""
    query = db.query(Senator).order_by(Senator.last_name, Senator.first_name)

    if is_active is not None:
        query = query.filter(Senator.is_active == is_active)
    if session is not None:
        query = query.filter(Senator.session_number == session)

    items, total = paginate(query, page=page, limit=limit)
    validated = [SenatorDTO.model_validate(_serialize_senator(senator, db)) for senator in items]
    return PaginatedResponse(items=validated, total=total, page=page, limit=limit)


@router.post("", response_model=SenatorDTO, status_code=status.HTTP_201_CREATED)
def create_admin_senator(
    body: CreateSenatorDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a senator record."""
    payload = body.model_dump()
    payload["district"] = payload.pop("district_id")

    senator = Senator(**payload)
    db.add(senator)
    db.commit()
    db.refresh(senator)
    return SenatorDTO.model_validate(_serialize_senator(senator, db))


@router.put(
    "/{senator_id}",
    response_model=SenatorDTO,
    responses={404: {"description": "Senator not found"}},
)
def update_admin_senator(
    senator_id: int,
    body: UpdateSenatorDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update senator fields. Unset fields remain unchanged."""
    senator = db.query(Senator).filter(Senator.id == senator_id).first()
    if senator is None:
        raise HTTPException(status_code=404, detail="Senator not found")

    update_data = body.model_dump(exclude_unset=True)
    if "district_id" in update_data:
        update_data["district"] = update_data.pop("district_id")

    for field, value in update_data.items():
        setattr(senator, field, value)

    db.commit()
    db.refresh(senator)
    return SenatorDTO.model_validate(_serialize_senator(senator, db))


@router.delete(
    "/{senator_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Senator not found"},
        409: {"description": "Linked leadership entries exist"},
    },
)
def delete_admin_senator(
    senator_id: int,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a senator, blocking deletion when leadership references still exist."""
    senator = db.query(Senator).filter(Senator.id == senator_id).first()
    if senator is None:
        raise HTTPException(status_code=404, detail="Senator not found")

    linked_leadership = db.query(Leadership).filter(Leadership.senator_id == senator_id).first()
    if linked_leadership is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Senator has linked leadership entries; update or delete leadership first",
        )

    db.query(CommitteeMembership).filter(CommitteeMembership.senator_id == senator_id).delete()
    db.delete(senator)
    db.commit()
    return None
