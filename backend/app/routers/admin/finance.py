"""Admin finance hearing CRUD routes.

PUT    /api/admin/finance-hearings/config       — update singleton config; updated_by from JWT
POST   /api/admin/finance-hearings/dates        — create hearing date
PUT    /api/admin/finance-hearings/dates/{id}   — update hearing date fields
DELETE /api/admin/finance-hearings/dates/{id}   — delete hearing date
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.FinanceHearingConfig import FinanceHearingConfig
from app.models.FinanceHearingDate import FinanceHearingDate
from app.schemas.finance import (
    CreateFinanceHearingDateDTO,
    FinanceHearingConfigDTO,
    FinanceHearingDateDTO,
    UpdateFinanceHearingConfigDTO,
    UpdateFinanceHearingDateDTO,
)

router = APIRouter(
    prefix="/api/admin/finance-hearings",
    tags=["admin", "finance"],
)


@router.put("/config", response_model=FinanceHearingConfigDTO)
def update_finance_config(
    body: UpdateFinanceHearingConfigDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update (or create) the singleton finance hearing configuration."""
    config = db.query(FinanceHearingConfig).first()
    if config is None:
        config = FinanceHearingConfig(
            is_active=body.is_active,
            season_start=body.season_start,
            season_end=body.season_end,
            updated_by=current_user.id,
        )
        db.add(config)
    else:
        config.is_active = body.is_active
        config.season_start = body.season_start
        config.season_end = body.season_end
        config.updated_by = current_user.id

    db.commit()
    db.refresh(config)

    dates = [
        FinanceHearingDateDTO.model_validate(d) for d in db.query(FinanceHearingDate).all()
    ] if config.is_active else []

    return FinanceHearingConfigDTO(
        is_active=config.is_active,
        season_start=config.season_start,
        season_end=config.season_end,
        dates=dates,
    )


@router.post(
    "/dates",
    response_model=FinanceHearingDateDTO,
    status_code=status.HTTP_201_CREATED,
)
def create_finance_date(
    body: CreateFinanceHearingDateDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a finance hearing date slot."""
    date_entry = FinanceHearingDate(**body.model_dump())
    db.add(date_entry)
    db.commit()
    db.refresh(date_entry)
    return FinanceHearingDateDTO.model_validate(date_entry)


@router.put(
    "/dates/{date_id}",
    response_model=FinanceHearingDateDTO,
    responses={404: {"description": "Hearing date not found"}},
)
def update_finance_date(
    date_id: int,
    body: UpdateFinanceHearingDateDTO,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update finance hearing date fields. Unset fields remain unchanged."""
    date_entry = db.query(FinanceHearingDate).filter(FinanceHearingDate.id == date_id).first()
    if date_entry is None:
        raise HTTPException(status_code=404, detail="Hearing date not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(date_entry, field, value)

    db.commit()
    db.refresh(date_entry)
    return FinanceHearingDateDTO.model_validate(date_entry)


@router.delete(
    "/dates/{date_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Hearing date not found"}},
)
def delete_finance_date(
    date_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a finance hearing date slot."""
    date_entry = db.query(FinanceHearingDate).filter(FinanceHearingDate.id == date_id).first()
    if date_entry is None:
        raise HTTPException(status_code=404, detail="Hearing date not found")

    db.delete(date_entry)
    db.commit()
    return None
