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

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_role
from app.models import (
    AppConfig,
    BudgetData,
    CalendarEvent,
    FinanceHearingConfig,
    News,
    StaticPageContent,
)
from app.models.Admin import Admin
from app.models.Sections import AdminSections, Sections
from app.schemas.account import (
    AccountDTO,
    AccountReferenceGroup,
    AccountReferenceItem,
    AccountReferencesDTO,
    CreateAccountDTO,
    UpdateAccountDTO,
)
from app.schemas.pagination import PaginatedResponse
from app.utils.pagination import paginate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/admin/accounts",
    tags=["admin", "accounts"],
)

# Records that hold a nullable "who touched this" reference to an admin
# account. Deleting the account sets these to NULL (see each model's FK),
# which silently erases the record's authorship/audit trail unless the
# admin doing the deleting sees this list first and reassigns them.
_REFERENCE_SPECS = [
    {
        "type": "news",
        "label": "News articles authored",
        "manage_url": "/admin/news",
        "model": News,
        "fk_column": "author_id",
        "item_label": lambda row: row.title,
    },
    {
        "type": "static_pages",
        "label": "Static pages edited",
        "manage_url": "/admin/static-pages",
        "model": StaticPageContent,
        "fk_column": "last_edited_by",
        "item_label": lambda row: row.title,
    },
    {
        "type": "app_config",
        "label": "App config entries updated",
        "manage_url": None,
        "model": AppConfig,
        "fk_column": "updated_by",
        "item_label": lambda row: row.key,
    },
    {
        "type": "budget_data",
        "label": "Budget entries updated",
        "manage_url": "/admin/budget",
        "model": BudgetData,
        "fk_column": "updated_by",
        "item_label": lambda row: f"{row.category} ({row.fiscal_year})",
    },
    {
        "type": "finance_hearing_config",
        "label": "Finance hearing settings updated",
        "manage_url": "/admin/finance-hearings",
        "model": FinanceHearingConfig,
        "fk_column": "updated_by",
        "item_label": lambda row: "Finance hearing settings",
    },
    {
        "type": "calendar_events",
        "label": "Calendar events created",
        "manage_url": "/admin/events",
        "model": CalendarEvent,
        "fk_column": "created_by",
        "item_label": lambda row: row.title,
    },
]

_MAX_ITEMS_PER_GROUP = 5


def _build_account_references(db: Session, account_id: int) -> list[AccountReferenceGroup]:
    groups: list[AccountReferenceGroup] = []
    for spec in _REFERENCE_SPECS:
        model = spec["model"]
        fk_column = getattr(model, spec["fk_column"])
        query = db.query(model).filter(fk_column == account_id)

        count = query.count()
        if count == 0:
            continue

        items = [
            AccountReferenceItem(id=row.id, label=spec["item_label"](row))
            for row in query.order_by(model.id).limit(_MAX_ITEMS_PER_GROUP).all()
        ]
        groups.append(
            AccountReferenceGroup(
                type=spec["type"],
                label=spec["label"],
                count=count,
                items=items,
                manage_url=spec["manage_url"],
                behavior="unlink",
            )
        )

    section_group = _build_section_membership_group(db, account_id)
    if section_group is not None:
        groups.append(section_group)

    return groups


def _build_section_membership_group(
    db: Session, account_id: int
) -> AccountReferenceGroup | None:
    """Section access assignments aren't a "who touched this" reference like
    the specs above — AdminSections.admin_id is ondelete=CASCADE, so these
    rows are deleted outright alongside the account, not nulled out. That
    makes them invisible to _build_account_references' spec loop even though
    deleting the account destroys them just the same, so they're surfaced
    here as a "remove" behavior rather than an "unlink" one.
    """
    query = (
        db.query(Sections)
        .join(AdminSections, AdminSections.section_id == Sections.id)
        .filter(AdminSections.admin_id == account_id)
    )

    count = query.count()
    if count == 0:
        return None

    items = [
        AccountReferenceItem(id=row.id, label=row.name)
        for row in query.order_by(Sections.id).limit(_MAX_ITEMS_PER_GROUP).all()
    ]
    return AccountReferenceGroup(
        type="section_memberships",
        label="Section access assignments",
        count=count,
        items=items,
        manage_url=None,
        behavior="remove",
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


@router.get(
    "/{account_id}/references",
    response_model=AccountReferencesDTO,
    responses={404: {"description": "Account not found"}},
)
def get_admin_account_references(
    account_id: int,
    _current_user: Admin = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List records that reference this account, so an admin can review or
    reassign them before deleting. Admin role required."""
    account = db.query(Admin).filter(Admin.id == account_id).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return AccountReferencesDTO(references=_build_account_references(db, account_id))


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
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Failed to delete account %s: %s", account_id, exc)
        raise HTTPException(
            status_code=409,
            detail="Cannot delete this account: it is still referenced by other records",
        )
    return None
