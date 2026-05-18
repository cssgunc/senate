"""Initialize a deployed database without deleting existing data.

Usage:
    python -m script.init_db

This script is intended for first deploys and safe redeploys. It creates any
missing tables and can optionally bootstrap the first admin account from
environment variables. It never drops tables and never clears application data.
"""

from __future__ import annotations

import os
import re
import sys

from sqlalchemy.exc import IntegrityError

from app.database import (
    Base,
    SessionLocal,
    engine,
)
from app.models import Admin  # noqa: F401 - importing app.models registers all tables
from app.static_pages import ensure_default_static_pages


def create_missing_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Missing tables created")


def bootstrap_initial_admin() -> None:
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    pid = os.getenv("INITIAL_ADMIN_PID")
    first_name = os.getenv("INITIAL_ADMIN_FIRST_NAME", "Initial")
    last_name = os.getenv("INITIAL_ADMIN_LAST_NAME", "Admin")
    role = os.getenv("INITIAL_ADMIN_ROLE", "admin")

    if not email and not pid:
        print("No initial admin requested")
        return

    if not email or not pid:
        print("INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_PID must be set together")
        sys.exit(1)

    if not re.fullmatch(r"\d{9}", pid):
        print("INITIAL_ADMIN_PID must be exactly 9 digits")
        sys.exit(1)

    if role not in {"admin", "staff"}:
        print("INITIAL_ADMIN_ROLE must be 'admin' or 'staff'")
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(Admin).filter(Admin.email == email).first()
        if existing:
            print(f"Initial admin '{email}' already exists")
            ensure_default_static_pages(db, editor=existing, commit=True)
            return

        admin = Admin(
            email=email,
            pid=pid,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        db.add(admin)
        db.flush()
        ensure_default_static_pages(db, editor=admin, commit=False)
        db.commit()
        print(f"Initial admin '{email}' created")
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
