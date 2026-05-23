from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin
from app.schemas.account import validate_onyen
from app.utils.auth import create_access_token, get_current_user, require_role
from app.utils.passwords import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    onyen: str
    password: str = Field(min_length=1)

    @field_validator("onyen")
    @classmethod
    def onyen_must_be_valid(cls, value: str) -> str:
        return validate_onyen(value)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Admin).filter(Admin.onyen == payload.onyen).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: Admin = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "onyen": current_user.onyen,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role,
    }


@router.get("/admin-only")
def admin_only_route(user=Depends(require_role("admin"))):
    return {"message": "Welcome, admin!"}
