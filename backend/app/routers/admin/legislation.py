from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_role
from app.models import Legislation, LegislationAction
from app.models.Admin import Admin
from app.schemas.legislation import (
    CreateLegislationActionDTO,
    CreateLegislationDTO,
    LegislationActionDTO,
    LegislationDTO,
    UpdateLegislationActionDTO,
    UpdateLegislationDTO,
)

router = APIRouter(
    prefix="/api/admin/legislation",
    tags=["admin", "legislation"],
)


def _load_actions(db: Session, legislation_id: int) -> list[LegislationAction]:
    return (
        db.query(LegislationAction)
        .filter(LegislationAction.legislation_id == legislation_id)
        .order_by(LegislationAction.display_order)
        .all()
    )


def _sync_last_action(db: Session, legislation: Legislation) -> None:
    latest_action_date = (
        db.query(func.max(LegislationAction.action_date))
        .filter(LegislationAction.legislation_id == legislation.id)
        .scalar()
    )
    legislation.date_last_action = latest_action_date or legislation.date_introduced

@router.post("", response_model=LegislationDTO)
def create_legislation(
    payload: CreateLegislationDTO,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(get_current_user),
):
    legislation = Legislation(
        **payload.model_dump(),
        date_last_action=payload.date_introduced # could change to be None
    )

    db.add(legislation)
    db.commit()
    db.refresh(legislation)

    legislation.actions = []

    return legislation

@router.put("/{id}", response_model=LegislationDTO)
def update_legislation(
    id: int,
    payload: UpdateLegislationDTO,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(get_current_user),
):
    legislation = db.query(Legislation).filter(Legislation.id == id).first()

    if not legislation:
        raise HTTPException(404, "Legislation not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(legislation, key):
            setattr(legislation, key, value)

    _sync_last_action(db, legislation)

    db.commit()
    db.refresh(legislation)

    legislation.actions = _load_actions(db, id)

    return legislation

@router.delete("/{id}", status_code=204)
def delete_legislation(
    id: int,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(require_role("admin")),
):
    legislation = db.query(Legislation).filter(Legislation.id == id).first()

    if not legislation:
        raise HTTPException(404, "Legislation not found")

    db.query(LegislationAction).filter(LegislationAction.legislation_id == id).delete(synchronize_session=False)

    db.delete(legislation)
    db.commit()

@router.post("/{id}/actions", response_model=LegislationActionDTO)
def add_action(
    id: int,
    payload: CreateLegislationActionDTO,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(get_current_user),
):
    legislation = (
        db.query(Legislation)
        .filter(Legislation.id == id)
        .first()
    )

    if not legislation:
        raise HTTPException(404, "Legislation not found")

    display_order = (
        db.query(LegislationAction)
        .filter(LegislationAction.legislation_id == id).all()
    )

    newDisplayOrder = -1
    for action in display_order:
        newDisplayOrder = max(newDisplayOrder, action.display_order)
    newDisplayOrder += 1

    action = LegislationAction(
        legislation_id=id,
        action_date=payload.action_date,
        description=payload.description,
        action_type=payload.action_type,
        display_order=newDisplayOrder,
    )

    db.add(action)

    legislation.date_last_action = payload.action_date

    db.commit()
    db.refresh(action)

    return action

@router.put("/{id}/actions/{action_id}", response_model=LegislationActionDTO)
def update_action(
    id: int,
    action_id: int,
    payload: UpdateLegislationActionDTO,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(get_current_user),
):
    action = (
        db.query(LegislationAction)
        .filter(
            LegislationAction.id == action_id,
            LegislationAction.legislation_id == id,
        )
        .first()
    )

    if not action:
        raise HTTPException(404, "Action not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(action, key):
            setattr(action, key, value)

    legislation = db.query(Legislation).filter(Legislation.id == id).first()
    if legislation is None:
        raise HTTPException(404, "Legislation not found")

    db.flush()
    _sync_last_action(db, legislation)

    db.commit()
    db.refresh(action)

    return action

@router.delete("/{id}/actions/{action_id}", status_code=204)
def delete_action(
    id: int,
    action_id: int,
    db: Session = Depends(get_db),
    _current_user: Admin = Depends(require_role("admin")),
):
    action = (
        db.query(LegislationAction)
        .filter(
            LegislationAction.id == action_id,
            LegislationAction.legislation_id == id,
        )
        .first()
    )

    if not action:
        raise HTTPException(404, "Action not found")

    legislation = db.query(Legislation).filter(Legislation.id == id).first()
    if legislation is None:
        raise HTTPException(404, "Legislation not found")

    db.delete(action)
    db.flush()
    _sync_last_action(db, legislation)
    db.commit()
