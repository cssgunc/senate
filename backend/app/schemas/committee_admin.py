from typing import Optional

from pydantic import BaseModel, EmailStr


class CommitteeCreateDTO(BaseModel):
    name: str
    description: str
    chair_name: str
    chair_email: EmailStr
    chair_senator_id: Optional[int] = None
    is_active: bool = True


class CommitteeUpdateDTO(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chair_name: Optional[str] = None
    chair_email: Optional[EmailStr] = None
    chair_senator_id: Optional[int] = None
    is_active: Optional[bool] = None


class AssignCommitteeMemberDTO(BaseModel):
    senator_id: int
    role: str = "Member"
