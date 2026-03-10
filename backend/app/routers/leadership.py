from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Leadership
from app.schemas import LeadershipDTO

router = APIRouter(prefix="/leadership", tags=["leadership"])

@router.get("/", response_model=list[LeadershipDTO])
def get_leadership(session_number: int | None = None, db: Session = Depends(get_db)):

    query = db.query(Leadership)

    if session_number:
        query = query.filter(Leadership.session_number == session_number)
    else:
        query = query.filter(Leadership.is_active)

    leadership = query.order_by(Leadership.title).all()

    # dynamically add is_current based on is_active
    for leader in leadership:
        leader.is_current = leader.is_active

    return leadership


@router.get("/{id}",  response_model=LeadershipDTO)
def get_leadership_by_id(id: int, db: Session = Depends(get_db)):

    leadership = (
        db.query(Leadership)
        .filter(Leadership.id == id)
        .first()
    )

    if leadership is None:
        raise HTTPException(status_code=404, detail="Leadership record not found")

    leadership.is_current = leadership.is_active

    return leadership
