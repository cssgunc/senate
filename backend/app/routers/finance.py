"""Finance hearings public API routes (TDD Section 4.5.2).

GET /api/finance-hearings — FinanceHearingConfig with nested dates when active
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.FinanceHearingConfig import FinanceHearingConfig
from app.models.FinanceHearingDate import FinanceHearingDate
from app.schemas.finance import FinanceHearingConfigDTO, FinanceHearingDateDTO

router = APIRouter(prefix="/api/finance-hearings", tags=["finance"])


@router.get("", response_model=FinanceHearingConfigDTO)
def get_finance_hearings(db: Session = Depends(get_db)):
    config = db.query(FinanceHearingConfig).first()
    if config is None:
        raise HTTPException(status_code=404, detail="Finance hearing configuration not found")

    dates: list[FinanceHearingDateDTO] = []
    if config.is_active:
        dates = [
            FinanceHearingDateDTO.model_validate(d) for d in db.query(FinanceHearingDate).all()
        ]

    return FinanceHearingConfigDTO(
        is_active=config.is_active,
        season_start=config.season_start,
        season_end=config.season_end,
        dates=dates,
    )
