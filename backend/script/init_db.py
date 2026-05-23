"""Initialize a deployed database without deleting existing data.

Usage:
    python -m script.init_db

This script is intended for first deploys and safe redeploys. It creates any
missing tables and can optionally bootstrap the first admin account from
environment variables. It never drops tables and never clears application data.
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError

from app.database import (
    Base,
    SessionLocal,
    engine,
)
from app.models import Admin  # noqa: F401 - importing app.models registers all tables
from app.schemas.account import MIN_PASSWORD_LENGTH, validate_onyen
from app.static_pages import ensure_default_static_pages
from app.utils.passwords import hash_password


def create_missing_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Missing tables created")


def bootstrap_initial_admin() -> None:
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    onyen = os.getenv("INITIAL_ADMIN_ONYEN")
    password = os.getenv("INITIAL_ADMIN_PASSWORD")
    first_name = os.getenv("INITIAL_ADMIN_FIRST_NAME", "Initial")
    last_name = os.getenv("INITIAL_ADMIN_LAST_NAME", "Admin")
    role = os.getenv("INITIAL_ADMIN_ROLE", "admin")

    if not email and not onyen and not password:
        print("No initial admin requested")
        return

    if not email or not onyen or not password:
        print(
            "INITIAL_ADMIN_EMAIL, INITIAL_ADMIN_ONYEN, and INITIAL_ADMIN_PASSWORD must be set together"
        )
        sys.exit(1)

    try:
        onyen = validate_onyen(onyen)
    except ValueError as exc:
        print(str(exc))
        sys.exit(1)

    if len(password) < MIN_PASSWORD_LENGTH:
        print(f"INITIAL_ADMIN_PASSWORD must be at least {MIN_PASSWORD_LENGTH} characters")
        sys.exit(1)

    if role not in {"admin", "staff"}:
        print("INITIAL_ADMIN_ROLE must be 'admin' or 'staff'")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(or_(Admin.email == email, Admin.onyen == onyen)).first()
        if existing:
            print(f"Initial admin {onyen} already exists")
            ensure_default_static_pages(db, editor=existing, commit=True)
            return

        admin = Admin(
            email=email,
            onyen=onyen,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        db.add(admin)
        db.flush()
        ensure_default_static_pages(db, editor=admin, commit=False)
        db.commit()
        print(f"Initial admin {onyen} created")
    except IntegrityError as exc:
        db.rollback()
        print(f"Could not create initial admin: {exc}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing deployed database")
    create_missing_tables()
    bootstrap_initial_admin()
    print("Database initialization complete")
