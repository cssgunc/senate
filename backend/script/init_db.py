"""Initialize a deployed database without deleting existing data.

Usage:
    python -m script.init_db

This script is intended for first deploys and safe redeploys. It creates the
target SQL Server database if it is missing, creates any missing tables, and can
optionally bootstrap the first admin account from environment variables.
It never drops tables and never clears application data.
"""

from __future__ import annotations

import os
import re
import sys

import pyodbc
from sqlalchemy.exc import IntegrityError

from app.database import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
    Base,
    SessionLocal,
    engine,
)
from app.models import Admin  # noqa: F401 - importing app.models registers all tables
from app.static_pages import ensure_default_static_pages


def _quote_sql_server_identifier(identifier: str) -> str:
    return f"[{identifier.replace(']', ']]')}]"


def create_database_if_missing() -> None:
    master_conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={DB_HOST},{DB_PORT};"
        "DATABASE=master;"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        "TrustServerCertificate=yes"
    )

    try:
        conn = pyodbc.connect(master_conn_str)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT database_id FROM sys.databases WHERE name = ?", DB_NAME)

        if cursor.fetchone():
            print(f"Database '{DB_NAME}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {_quote_sql_server_identifier(DB_NAME)}")
            print(f"Database '{DB_NAME}' created")

        cursor.close()
        conn.close()
    except pyodbc.Error as exc:
        print(f"Could not initialize database '{DB_NAME}': {exc}")
        sys.exit(1)


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
    create_database_if_missing()
    create_missing_tables()
    bootstrap_initial_admin()
    print("Database initialization complete")
