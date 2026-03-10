"""Budget public API routes (TDD Section 4.5.2).

GET /api/budget — hierarchical BudgetData; filterable by fiscal_year; defaults to most recent
"""

import re
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.BudgetData import BudgetData
from app.schemas.budget import BudgetDataDTO

router = APIRouter(prefix="/api/budget", tags=["budget"])


def _fiscal_year_sort_key(fiscal_year: str) -> tuple[int, str]:
    """Sort fiscal year labels by numeric suffix first, then raw value."""
    matches = re.findall(r"\d+", fiscal_year)
    numeric_year = int(matches[-1]) if matches else -1
    return numeric_year, fiscal_year


def _build_tree(
    row_id: int,
    rows_by_id: dict[int, BudgetData],
    children_map: dict[int, list[BudgetData]],
) -> BudgetDataDTO:
    row = rows_by_id[row_id]
    children = [
        _build_tree(child.id, rows_by_id, children_map) for child in children_map.get(row_id, [])
    ]
    return BudgetDataDTO(
        id=row.id,
        fiscal_year=row.fiscal_year,
        category=row.category,
        amount=float(row.amount),
        description=row.description,
        children=children,
    )


@router.get("", response_model=list[BudgetDataDTO])
def list_budget(
    fiscal_year: Optional[str] = Query(default=None, description="Fiscal year filter"),
    db: Session = Depends(get_db),
):
    if fiscal_year is None:
        fiscal_years = [row[0] for row in db.query(BudgetData.fiscal_year).distinct().all()]
        if not fiscal_years:
            return []
        fiscal_year = max(fiscal_years, key=_fiscal_year_sort_key)

    rows = (
        db.query(BudgetData)
        .filter(BudgetData.fiscal_year == fiscal_year)
        .order_by(BudgetData.display_order)
        .all()
    )

    rows_by_id = {row.id: row for row in rows}
    children_map: dict[int, list[BudgetData]] = {row.id: [] for row in rows}
    roots: list[BudgetData] = []

    for row in rows:
        if row.parent_category_id is None:
            roots.append(row)
        elif row.parent_category_id in children_map:
            children_map[row.parent_category_id].append(row)

    return [_build_tree(r.id, rows_by_id, children_map) for r in roots]
