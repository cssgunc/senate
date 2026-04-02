from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Leadership
from app.schemas.leadership import LeadershipDTO

router = APIRouter(prefix="/api/leadership", tags=["leadership"])


def _current_session(db: Session) -> int:
    """Return the highest session_number in the leadership table."""
    result = db.query(func.max(Leadership.session_number)).scalar()
    return result or 1


@router.get("/", response_model=list[LeadershipDTO])
def get_leadership(session_number: int | None = None, db: Session = Depends(get_db)):

    target_session = session_number if session_number is not None else _current_session(db)
    query = db.query(Leadership).filter(Leadership.session_number == target_session)

    leadership = query.order_by(Leadership.title).all()

    # dynamically add is_current based on is_active
    for leader in leadership:
        leader.is_current = leader.is_active
        leader.photo_url = leader.headshot_url

    return leadership


@router.get("/{id}", response_model=LeadershipDTO)
def get_leadership_by_id(id: int, db: Session = Depends(get_db)):

    leadership = db.query(Leadership).filter(Leadership.id == id).first()

    if leadership is None:
        raise HTTPException(status_code=404, detail="Leadership record not found")

    leadership.is_current = leadership.is_active
    leadership.photo_url = leadership.headshot_url

    return leadership
