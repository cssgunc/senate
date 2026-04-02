from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models.cms import Committee, CommitteeMembership
from app.models.Senator import Senator
from app.schemas.committee import CommitteeDTO
from app.schemas.committee_admin import (
    AssignCommitteeMemberDTO,
    CommitteeCreateDTO,
    CommitteeUpdateDTO,
)

router = APIRouter(
    prefix="/api/admin/committees",
    tags=["admin", "committees"],
)


# Mock auth dependency since the auth ticket isn't ready
def mock_auth_dependency() -> Any:
    # TODO: Replace with actual JWT authentication when completed
    return True


def serialize_committee(committee: Committee) -> dict:
    members = []
    # If memberships are loaded
    if hasattr(committee, "memberships"):
        for membership in committee.memberships:
            senator = membership.senator
            members.append(
                {
                    "id": senator.id,
                    "first_name": senator.first_name,
                    "last_name": senator.last_name,
                    "email": senator.email,
                    "headshot_url": senator.headshot_url,
                    "district_id": senator.district,
                    "is_active": senator.is_active,
                    "session_number": senator.session_number,
                    "committees": [
                        {
                            "committee_id": membership.committee.id,
                            "committee_name": membership.committee.name,
                            "role": membership.role,
                        }
                    ],
                }
            )

    return {
        "id": committee.id,
        "name": committee.name,
        "description": committee.description,
        "chair_name": committee.chair_name,
        "chair_email": committee.chair_email,
        "members": members,
        "is_active": committee.is_active,
    }


@router.post("", response_model=CommitteeDTO, status_code=status.HTTP_201_CREATED)
def create_committee(
    data: CommitteeCreateDTO,
    db: Session = Depends(get_db),
    _auth: Any = Depends(mock_auth_dependency),
):
    new_committee = Committee(**data.model_dump())
    db.add(new_committee)
    db.commit()
    db.refresh(new_committee)
    # Give it an empty standard memberships list so it serializes properly
    new_committee.memberships = []
    return serialize_committee(new_committee)


@router.put("/{committee_id}", response_model=CommitteeDTO)
def update_committee(
    committee_id: int,
    data: CommitteeUpdateDTO,
    db: Session = Depends(get_db),
    _auth: Any = Depends(mock_auth_dependency),
):
    committee = (
        db.query(Committee)
        .options(selectinload(Committee.memberships).selectinload(CommitteeMembership.senator))
        .filter(Committee.id == committee_id)
        .first()
    )
    if not committee:
        raise HTTPException(status_code=404, detail="Committee not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(committee, key, value)

    db.commit()
    db.refresh(committee)
    return serialize_committee(committee)


@router.delete("/{committee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_committee(
    committee_id: int, db: Session = Depends(get_db), _auth: Any = Depends(mock_auth_dependency)
):
    committee = db.query(Committee).filter(Committee.id == committee_id).first()
    if not committee:
        raise HTTPException(status_code=404, detail="Committee not found")

    db.delete(committee)
    db.commit()
    return None


@router.post("/{committee_id}/members", status_code=status.HTTP_201_CREATED)
def add_committee_member(
    committee_id: int,
    data: AssignCommitteeMemberDTO,
    db: Session = Depends(get_db),
    _auth: Any = Depends(mock_auth_dependency),
):
    committee = db.query(Committee).filter(Committee.id == committee_id).first()
    if not committee:
        raise HTTPException(status_code=404, detail="Committee not found")

    senator = db.query(Senator).filter(Senator.id == data.senator_id).first()
    if not senator:
        raise HTTPException(status_code=404, detail="Senator not found")

    membership = (
        db.query(CommitteeMembership)
        .filter(
            CommitteeMembership.committee_id == committee_id,
            CommitteeMembership.senator_id == data.senator_id,
        )
        .first()
    )

    if membership:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Senator is already a member of this committee",
        )

    new_membership = CommitteeMembership(
        committee_id=committee_id, senator_id=data.senator_id, role=data.role
    )
    db.add(new_membership)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Senator is already a member of this committee",
        )

    return {"message": "Member added successfully"}


@router.delete("/{committee_id}/members/{senator_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_committee_member(
    committee_id: int,
    senator_id: int,
    db: Session = Depends(get_db),
    _auth: Any = Depends(mock_auth_dependency),
):
    membership = (
        db.query(CommitteeMembership)
        .filter(
            CommitteeMembership.committee_id == committee_id,
            CommitteeMembership.senator_id == senator_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")

    db.delete(membership)
    db.commit()
    return None
