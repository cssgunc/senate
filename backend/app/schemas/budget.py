"""Budget data schemas — input and output DTOs."""

from pydantic import BaseModel, ConfigDict, field_validator


class BudgetDataDTO(BaseModel):
    id: int
    fiscal_year: str
    category: str
    amount: float
    description: str | None
    children: list["BudgetDataDTO"]

    model_config = ConfigDict(from_attributes=True)


BudgetDataDTO.model_rebuild()


class CreateBudgetDataDTO(BaseModel):
    fiscal_year: str
    category: str
    amount: float
    description: str | None
    parent_category_id: int | None
    display_order: int

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v
