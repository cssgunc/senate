"""Admin budget CRUD routes.

GET    /api/admin/budget       — flat list; optional fiscal_year filter
POST   /api/admin/budget       — create budget entry; updated_by set from JWT
PUT    /api/admin/budget/{id}  — update budget entry fields
DELETE /api/admin/budget/{id}  — delete budget entry
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.Admin import Admin
from app.models.BudgetData import BudgetData
from app.schemas.budget import AdminBudgetDataDTO, CreateBudgetDataDTO, UpdateBudgetDataDTO

router = APIRouter(
    prefix="/api/admin/budget",
    tags=["admin", "budget"],
)


@router.get("", response_model=list[AdminBudgetDataDTO])
def list_admin_budget(
    fiscal_year: Optional[str] = Query(default=None, description="Filter by fiscal year"),
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return a flat list of all budget entries, optionally filtered by fiscal year."""
    query = db.query(BudgetData).order_by(BudgetData.display_order)
    if fiscal_year is not None:
        query = query.filter(BudgetData.fiscal_year == fiscal_year)
    return [AdminBudgetDataDTO.model_validate(row) for row in query.all()]


@router.post("", response_model=AdminBudgetDataDTO, status_code=status.HTTP_201_CREATED)
def create_admin_budget(
    body: CreateBudgetDataDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a budget entry. updated_by is set from the authenticated user."""
    if body.parent_category_id is not None:
        parent = db.query(BudgetData).filter(BudgetData.id == body.parent_category_id).first()
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")

    entry = BudgetData(**body.model_dump(), updated_by=current_user.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return AdminBudgetDataDTO.model_validate(entry)


@router.put(
    "/{budget_id}",
    response_model=AdminBudgetDataDTO,
    responses={404: {"description": "Budget entry not found"}},
)
def update_admin_budget(
    budget_id: int,
    body: UpdateBudgetDataDTO,
    current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update budget entry fields. Unset fields remain unchanged."""
    entry = db.query(BudgetData).filter(BudgetData.id == budget_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Budget entry not found")

    update_data = body.model_dump(exclude_unset=True)

    if "parent_category_id" in update_data and update_data["parent_category_id"] is not None:
        if update_data["parent_category_id"] == budget_id:
            raise HTTPException(status_code=400, detail="Budget entry cannot be its own parent")
        parent = db.query(BudgetData).filter(
            BudgetData.id == update_data["parent_category_id"]
        ).first()
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent category not found")

    for field, value in update_data.items():
        setattr(entry, field, value)
    entry.updated_by = current_user.id

    db.commit()
    db.refresh(entry)
    return AdminBudgetDataDTO.model_validate(entry)


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"description": "Budget entry not found"},
        409: {"description": "Budget entry has child entries"},
    },
)
def delete_admin_budget(
    budget_id: int,
    _current_user: Admin = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a budget entry. Blocked if it has child entries."""
    entry = db.query(BudgetData).filter(BudgetData.id == budget_id).first()
    if entry is None:
        raise HTTPException(status_code=404, detail="Budget entry not found")

    child = db.query(BudgetData).filter(BudgetData.parent_category_id == budget_id).first()
    if child is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Budget entry has child entries; delete or reparent them first",
        )

    db.delete(entry)
    db.commit()
    return None
