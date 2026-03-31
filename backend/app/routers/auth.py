from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin
from app.utils.auth import create_access_token, get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(email: str, pid: str, db: Session = Depends(get_db)):
    user = db.query(Admin).filter(Admin.email == email).first()

    if not user or user.pid != pid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(current_user: Admin = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
    }


@router.get("/admin-only")
def admin_only_route(user=Depends(require_role("admin"))):
    return {"message": "Welcome, admin!"}
