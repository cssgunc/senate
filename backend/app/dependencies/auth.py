"""Authentication dependencies.

get_current_user and require_role are stubs until #61 (auth) is implemented.
All admin routes depend on get_current_user; overriding it in tests is sufficient
to exercise role-checking logic because require_role calls Depends(get_current_user)
internally, and FastAPI resolves dependency_overrides at request time.
"""

from fastapi import Depends, HTTPException

from app.models.Admin import Admin


def get_current_user() -> Admin:
    """Return the authenticated Admin derived from the request JWT.

    TODO: Implement full JWT verification in #61.
    """
    raise HTTPException(status_code=501, detail="Authentication not yet implemented")


def require_role(role: str):
    """Return a dependency that enforces *role* on the current user."""

    def dependency(current_user: Admin = Depends(get_current_user)) -> Admin:
        if current_user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return dependency
