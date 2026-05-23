from datetime import datetime, timedelta
from typing import Dict, List, Tuple

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Admin
from app.schemas.account import MAX_PASSWORD_LENGTH, validate_onyen
from app.utils.auth import create_access_token, get_current_user, require_role
from app.utils.passwords import verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

MAX_FAILED_LOGIN_ATTEMPTS = 5
FAILED_LOGIN_WINDOW = timedelta(minutes=15)
failed_login_attempts: Dict[Tuple[str, str], List[datetime]] = {}


class LoginRequest(BaseModel):
    onyen: str
    password: str = Field(min_length=1, max_length=MAX_PASSWORD_LENGTH)

    @field_validator("onyen")
    @classmethod
    def onyen_must_be_valid(cls, value: str) -> str:
        return validate_onyen(value)


def _login_rate_limit_key(request: Request, onyen: str) -> tuple[str, str]:
    client_ip = request.client.host if request.client else "unknown"
    return client_ip, onyen


def check_login_rate_limit(request: Request, onyen: str) -> None:
    key = _login_rate_limit_key(request, onyen)
    now = datetime.now()
    cutoff_time = now - FAILED_LOGIN_WINDOW
    attempts = [attempt for attempt in failed_login_attempts.get(key, []) if attempt > cutoff_time]
    failed_login_attempts[key] = attempts

    if len(attempts) >= MAX_FAILED_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again later.",
        )


def record_failed_login(request: Request, onyen: str) -> None:
    key = _login_rate_limit_key(request, onyen)
    failed_login_attempts.setdefault(key, []).append(datetime.now())


def clear_failed_logins(request: Request, onyen: str) -> None:
    failed_login_attempts.pop(_login_rate_limit_key(request, onyen), None)


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    check_login_rate_limit(request, payload.onyen)
    user = db.query(Admin).filter(Admin.onyen == payload.onyen).first()

    if not user or not verify_password(payload.password, user.password_hash):
        record_failed_login(request, payload.onyen)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    clear_failed_logins(request, payload.onyen)
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
