from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Committee, CommitteeMembership
from app.schemas.committee import CommitteeDTO

router = APIRouter(prefix="/api/committees", tags=["committees"])


@router.get("/", response_model=list[CommitteeDTO])
def get_committees(db: Session = Depends(get_db)):
    committees = (
        db.query(Committee)
        .options(selectinload(Committee.memberships).selectinload(CommitteeMembership.senator))
        .filter(Committee.is_active)
        .order_by(Committee.name)
        .all()
    )

    result = []
    for committee in committees:
        members = []
        for membership in committee.memberships:
            senator = membership.senator
            committees_list = [
                {
                    "committee_id": membership.committee.id,
                    "committee_name": membership.committee.name,
                    "role": membership.role,
                }
            ]
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
                    "committees": committees_list,
                }
            )
        result.append(
            {
                "id": committee.id,
                "name": committee.name,
                "description": committee.description,
                "chair_name": committee.chair_name,
                "chair_email": committee.chair_email,
                "is_active": committee.is_active,
                "members": members,
            }
        )

    return result


@router.get("/{id}", response_model=CommitteeDTO)
def get_committee(id: int, db: Session = Depends(get_db)):
    committee = (
        db.query(Committee)
        .options(selectinload(Committee.memberships).selectinload(CommitteeMembership.senator))
        .filter(Committee.id == id)
        .first()
    )

    if not committee:
        raise HTTPException(status_code=404, detail="Committee not found")

    members = []

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
