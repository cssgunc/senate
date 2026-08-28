"""Admin account management routes (admin role required for all).

GET    /api/admin/accounts       — paginated list of admin/staff accounts
POST   /api/admin/accounts       — create account
PUT    /api/admin/accounts/{id}  — update account fields
DELETE /api/admin/accounts/{id}  — delete account

Any admin can create, edit, or delete any other admin or staff account,
including changing roles — there is no hierarchy beyond the flat admin/staff
split. The one guardrail is that the last remaining admin account can never
be deleted or demoted to staff, so account management can never lock itself
out. Self-deletion is also blocked.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_role
from app.models.Admin import Admin
from app.schemas.account import AccountDTO, CreateAccountDTO, UpdateAccountDTO
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate

router = APIRouter(
    prefix="/api/admin/accounts",
    tags=["admin", "accounts"],
)


def _other_admin_exists(db: Session, excluding_id: int) -> bool:
    return (
        db.query(Admin)
        .filter(Admin.role == "admin", Admin.id != excluding_id)
        .first()
        is not None
    )


@router.get("", response_model=PaginatedResponse[AccountDTO])
def list_admin_accounts(
    page: int = Query(default=1, ge=1, description="1-based page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Return a paginated list of all accounts. Admin role required."""
    query = db.query(Admin).order_by(Admin.last_name, Admin.first_name)
    items, total = paginate(query, page=page, limit=limit)
    return PaginatedResponse(
        items=[AccountDTO.model_validate(a) for a in items],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=AccountDTO, status_code=status.HTTP_201_CREATED)
def create_admin_account(
    body: CreateAccountDTO,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create an admin or staff account. Admin role required."""
    account = Admin(**body.model_dump())
    db.add(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Account with that email or Onyen already exists",
        )
    db.refresh(account)
    return AccountDTO.model_validate(account)


@router.put(
    "/{account_id}",
    response_model=AccountDTO,
    responses={404: {"description": "Account not found"}},
)
def update_admin_account(
    account_id: int,
    body: UpdateAccountDTO,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update account fields. Unset fields remain unchanged. Admin role required."""
    account = db.query(Admin).filter(Admin.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    fields = body.model_dump(exclude_unset=True)
    demoting_last_admin = (
        account.role == "admin"
        and fields.get("role", "admin") != "admin"
        and not _other_admin_exists(db, excluding_id=account.id)
    )
    if demoting_last_admin:
        raise HTTPException(
            status_code=400,
            detail="Cannot change the role of the last admin account",
        )

    for field, value in fields.items():
        setattr(account, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Update would conflict with an existing account (duplicate email or Onyen)",
        )
    db.refresh(account)
    return AccountDTO.model_validate(account)


@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Account not found"}},
)
def delete_admin_account(
    account_id: int,
    current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Delete an account. Admin role required. Cannot delete your own account
    or the last remaining admin account."""
    if account_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    account = db.query(Admin).filter(Admin.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    if account.role == "admin" and not _other_admin_exists(db, excluding_id=account.id):
        raise HTTPException(status_code=400, detail="Cannot delete the last admin account")

    db.delete(account)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this account: it is still referenced by other records",
        )
    return None
