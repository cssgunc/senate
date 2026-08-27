import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.config import ENVIRONMENT, FRONTEND_BASE_URL
from app.database import get_db
from app.models import Admin
from app.saml import (
    build_saml_auth,
    build_saml_request_data,
    extract_onyen,
    saml_configured,
)
from app.schemas.account import validate_onyen
from app.utils.auth import create_access_token, get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)


class DevLoginRequest(BaseModel):
    onyen: str

    @field_validator("onyen")
    @classmethod
    def onyen_must_be_valid(cls, value: str) -> str:
        return validate_onyen(value)


@router.post("/dev-login")
def dev_login(payload: DevLoginRequest, db: Session = Depends(get_db)):
    """Local-only login bypass for onyens already on the accounts allowlist.

    Stands in for the real SSO round-trip during development, since there's
    no way to hit UNC's IdP from a non-registered dev/staging environment.
    Never available in production — SAML SSO is the only login path there.
    """
    if ENVIRONMENT == "production":
        raise HTTPException(status_code=404)

    user = db.query(Admin).filter(Admin.onyen == payload.onyen).first()
    if not user:
        raise HTTPException(status_code=401, detail="No account with that onyen")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


def _request_port(request: Request) -> int:
    if request.url.port:
        return request.url.port
    return 443 if request.url.scheme == "https" else 80


@router.get("/saml/login")
async def saml_login_redirect(request: Request, next: str = "/admin"):
    if not saml_configured():
        raise HTTPException(
            status_code=503,
            detail="Onyen SSO is not yet configured. Contact an admin.",
        )

    request_data = build_saml_request_data(
        scheme=request.url.scheme,
        host=request.url.hostname or "",
        port=_request_port(request),
        path=request.url.path,
        get_params=dict(request.query_params),
        post_params={},
    )
    auth = build_saml_auth(request_data)
    redirect_url = auth.login(return_to=next)
    return RedirectResponse(redirect_url)


@router.post("/saml/acs")
async def saml_acs(request: Request, db: Session = Depends(get_db)):
    if not saml_configured():
        raise HTTPException(status_code=503, detail="Onyen SSO is not yet configured.")

    form = await request.form()
    post_params = dict(form)

    request_data = build_saml_request_data(
        scheme=request.url.scheme,
        host=request.url.hostname or "",
        port=_request_port(request),
        path=request.url.path,
        get_params=dict(request.query_params),
        post_params=post_params,
    )
    auth = build_saml_auth(request_data)
    auth.process_response()

    errors = auth.get_errors()
    if errors:
        logger.warning("SAML ACS validation failed: %s", auth.get_last_error_reason())
        raise HTTPException(status_code=401, detail="SSO sign-in failed. Contact an admin.")

    if not auth.is_authenticated():
        raise HTTPException(status_code=401, detail="SSO sign-in failed.")

    attributes = auth.get_attributes()
    name_id = auth.get_nameid()
    onyen = extract_onyen(attributes, name_id)

    logger.info("SAML login attempt. NameID=%s onyen=%s attributes=%s", name_id, onyen, attributes)

    user = db.query(Admin).filter(Admin.onyen == onyen).first() if onyen else None
    next_path = post_params.get("RelayState") or "/admin"

    if not user:
        logger.info("SAML login rejected — %r is not on the accounts allowlist", onyen)
        return RedirectResponse(f"{FRONTEND_BASE_URL}/admin/login?error=no_access", status_code=303)

    token = create_access_token(data={"sub": str(user.id)})
    return RedirectResponse(
        f"{FRONTEND_BASE_URL}/admin/sso-callback#token={token}&next={next_path}",
        status_code=303,
    )


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
