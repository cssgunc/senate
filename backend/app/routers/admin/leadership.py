"""Admin leadership CRUD routes.

GET    /api/admin/leadership       — paginated list; optional session_number filter
POST   /api/admin/leadership       — create leadership entry
PUT    /api/admin/leadership/{id}  — update leadership entry
DELETE /api/admin/leadership/{id}  — delete leadership entry (admin role required)
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.Admin import Admin
from app.models.Leadership import Leadership
from app.models.Senator import Senator
from app.schemas.leadership import CreateLeadershipDTO, LeadershipDTO, UpdateLeadershipDTO
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(
    prefix="/api/admin/leadership",
    tags=["admin", "leadership"],
)


def _serialize_leadership(leader: Leadership) -> dict[str, Any]:
    return {
        "id": leader.id,
        "senator_id": leader.senator_id,
        "title": leader.title,
        "first_name": leader.first_name,
        "last_name": leader.last_name,
        "email": leader.email,
        "photo_url": leader.headshot_url,
        "session_number": leader.session_number,
        "is_current": leader.is_active,
    }


@router.get("", response_model=PaginatedResponse[LeadershipDTO])
def list_admin_leadership(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    session_number: int | None = Query(default=None, description="Filter by session number"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return paginated leadership entries for admin workflows."""
    query = db.query(Leadership).order_by(Leadership.session_number.desc(), Leadership.title)

    if session_number is not None:
        query = query.filter(Leadership.session_number == session_number)

    items, total = paginate(query, page=page, limit=limit)
    validated = [LeadershipDTO.model_validate(_serialize_leadership(leader)) for leader in items]
    return PaginatedResponse(items=validated, total=total, page=page, limit=limit)


@router.post("", response_model=LeadershipDTO, status_code=status.HTTP_201_CREATED)
def create_admin_leadership(
    body: CreateLeadershipDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a leadership entry."""
    if body.senator_id is not None:
        senator = db.query(Senator).filter(Senator.id == body.senator_id).first()
        if senator is None:
            raise HTTPException(status_code=404, detail="Senator not found")

    leader = Leadership(**body.model_dump())
    db.add(leader)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to create leadership due to invalid data")
    db.refresh(leader)
    return LeadershipDTO.model_validate(_serialize_leadership(leader))


@router.put(
    "/{leadership_id}",
    response_model=LeadershipDTO,
    responses={404: {"description": "Leadership record not found"}},
)
def update_admin_leadership(
    leadership_id: int,
    body: UpdateLeadershipDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update leadership fields. Unset fields remain unchanged."""
    leader = db.query(Leadership).filter(Leadership.id == leadership_id).first()
    if leader is None:
        raise HTTPException(status_code=404, detail="Leadership record not found")

    update_data = body.model_dump(exclude_unset=True)
    if "senator_id" in update_data and update_data["senator_id"] is not None:
        senator = db.query(Senator).filter(Senator.id == update_data["senator_id"]).first()
        if senator is None:
            raise HTTPException(status_code=404, detail="Senator not found")

    for field, value in update_data.items():
        setattr(leader, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Unable to update leadership due to invalid data")
    db.refresh(leader)
    return LeadershipDTO.model_validate(_serialize_leadership(leader))


@router.delete(
    "/{leadership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Leadership record not found"}},
)
def delete_admin_leadership(
    leadership_id: int,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a leadership entry."""
    leader = db.query(Leadership).filter(Leadership.id == leadership_id).first()
    if leader is None:
        raise HTTPException(status_code=404, detail="Leadership record not found")

    db.delete(leader)
    db.commit()
    return None
