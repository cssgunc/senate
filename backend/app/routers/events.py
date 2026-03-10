"""Calendar events public API routes (TDD Section 4.5.2).

GET /api/events — published events only; filterable by start_date, end_date, event_type
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.CalendarEvent import CalendarEvent
from app.schemas.calendar_event import CalendarEventDTO

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=list[CalendarEventDTO])
def list_events(
    start_date: Optional[date] = Query(default=None, description="Include events on or after this date"),
    end_date: Optional[date] = Query(default=None, description="Include events on or before this date"),
    event_type: Optional[str] = Query(default=None, description="Filter by event type"),
    db: Session = Depends(get_db),
):
    query = db.query(CalendarEvent).filter(CalendarEvent.is_published.is_(True))

    if start_date is not None:
        query = query.filter(CalendarEvent.start_datetime >= start_date)
    if end_date is not None:
        query = query.filter(CalendarEvent.start_datetime < end_date + timedelta(days=1))
    if event_type is not None:
        query = query.filter(CalendarEvent.event_type == event_type)

    events = query.order_by(CalendarEvent.start_datetime).all()
    return [CalendarEventDTO.model_validate(e) for e in events]
