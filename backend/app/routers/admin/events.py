"""Admin calendar event CRUD routes.

POST   /api/admin/events       — create event; created_by set from JWT
PUT    /api/admin/events/{id}  — update event fields
DELETE /api/admin/events/{id}  — delete event (admin role required)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models.Admin import Admin
from app.models.CalendarEvent import CalendarEvent
from app.schemas.calendar_event import (
    AdminCalendarEventDTO,
    CreateAdminCalendarEventDTO,
    UpdateCalendarEventDTO,
)

router = APIRouter(
    prefix="/api/admin/events",
    tags=["admin", "events"],
)


@router.post("", response_model=AdminCalendarEventDTO, status_code=status.HTTP_201_CREATED)
def create_admin_event(
    body: CreateAdminCalendarEventDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a calendar event. created_by is set from the authenticated user."""
    event = CalendarEvent(**body.model_dump(), created_by=current_user.id)
    db.add(event)
    db.commit()
    db.refresh(event)
    return AdminCalendarEventDTO.model_validate(event)


@router.put(
    "/{event_id}",
    response_model=AdminCalendarEventDTO,
    responses={404: {"description": "Event not found"}},
)
def update_admin_event(
    event_id: int,
    body: UpdateCalendarEventDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update event fields. Unset fields remain unchanged."""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return AdminCalendarEventDTO.model_validate(event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Event not found"}},
)
def delete_admin_event(
    event_id: int,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete a calendar event. Requires admin role."""
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    db.delete(event)
    db.commit()
    return None
