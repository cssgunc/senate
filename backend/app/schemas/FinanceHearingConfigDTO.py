from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .FinanceHearingDateDTO import FinanceHearingDateDTO


class FinanceHearingConfigDTO(BaseModel):
    is_active: bool
    season_start: Optional[date] = None
    season_end: Optional[date] = None
    dates: List[FinanceHearingDateDTO]

    model_config = ConfigDict(from_attributes=True)
