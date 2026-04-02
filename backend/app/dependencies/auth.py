"""Authentication dependencies.

Thin wrapper around the canonical implementations in ``app.utils.auth``.
Importing from this module keeps dependency paths stable across routers/tests.
"""

from app.utils.auth import get_current_user, require_role

__all__ = ["get_current_user", "require_role"]
