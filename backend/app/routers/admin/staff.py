"""Admin staff CRUD routes.

POST   /api/admin/staff       — create staff member
PUT    /api/admin/staff/{id}  — update staff fields
DELETE /api/admin/staff/{id}  — delete staff member
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.cms import Staff
from app.schemas.staff import CreateStaffDTO, StaffDTO, UpdateStaffDTO

router = APIRouter(
    prefix="/api/admin/staff",
    tags=["admin", "staff"],
)


@router.post("", response_model=StaffDTO, status_code=status.HTTP_201_CREATED)
def create_admin_staff(
    body: CreateStaffDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a staff member."""
    staff = Staff(**body.model_dump())
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return StaffDTO.model_validate(staff)


@router.put(
    "/{staff_id}",
    response_model=StaffDTO,
    responses={404: {"description": "Staff member not found"}},
)
def update_admin_staff(
    staff_id: int,
    body: UpdateStaffDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update staff fields. Unset fields remain unchanged."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff member not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)
    return StaffDTO.model_validate(staff)


@router.delete(
    "/{staff_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Staff member not found"}},
)
def delete_admin_staff(
    staff_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a staff member."""
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if staff is None:
        raise HTTPException(status_code=404, detail="Staff member not found")

    db.delete(staff)
    db.commit()
    return None
