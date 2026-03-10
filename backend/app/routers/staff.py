"""Staff public API routes (TDD Section 4.5.2).

GET /api/staff — active staff ordered by display_order
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cms import Staff
from app.schemas.staff import StaffDTO

router = APIRouter(prefix="/api/staff", tags=["staff"])


@router.get("", response_model=list[StaffDTO])
def list_staff(db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.is_active.is_(True)).order_by(Staff.display_order).all()
    return [StaffDTO.model_validate(s) for s in staff]
