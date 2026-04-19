from fastapi import Depends, HTTPException, status


def get_current_user():
    """Return the current user or raise 401 when not provided.

    Tests should override this dependency when they need to simulate an
    authenticated user (app.dependency_overrides[get_current_user] = ...).
    """
    from fastapi import HTTPException
    from starlette import status

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def require_role(role: str):
    """Return a dependency that ensures the current user exists and has the
    required role. This mirrors production behavior sufficiently for tests.
    """

    def _inner(_current_user = Depends(get_current_user)):
        if _current_user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        # assume _current_user has attribute `role` set to 'admin' or 'staff'
        user_role = getattr(_current_user, "role", None)
        if user_role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return _current_user

    return _inner
