from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BudgetDataDTO(BaseModel):
    id: int
    fiscal_year: str
    category: str
    amount: float
    description: Optional[str] = None
    children: List["BudgetDataDTO"] = []

    model_config = ConfigDict(from_attributes=True)


BudgetDataDTO.model_rebuild()
