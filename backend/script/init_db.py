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

from sqlalchemy import inspect, or_, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateColumn, CreateIndex

from app.database import (
    Base,
    SessionLocal,
    engine,
)
from app.models import Admin  # noqa: F401 - importing app.models registers all tables
from app.schemas.account import validate_onyen
from app.static_pages import ensure_default_static_pages


def create_missing_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Missing tables created")


def sync_missing_columns() -> None:
    """Add columns present on the ORM models but missing from deployed tables.

    create_all() only creates tables that don't exist yet; it never alters a
    table that's already there. When a column is added to a model whose table
    was already deployed, the deployed table silently falls out of sync and
    any insert/update touching that column fails at the database level. This
    brings existing tables' columns back in line with the models.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # just created by create_missing_tables()

            existing_columns = {col["name"] for col in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing_columns:
                    continue

                if not column.nullable and column.default is None and column.server_default is None:
                    print(
                        f"Skipping {table.name}.{column.name}: NOT NULL with no default, "
                        "cannot be added automatically to a table with existing rows"
                    )
                    continue

                column_ddl = CreateColumn(column).compile(dialect=engine.dialect)
                conn.execute(text(f"ALTER TABLE {table.name} ADD COLUMN {column_ddl}"))
                print(f"Added missing column {table.name}.{column.name}")

            # A column that already exists but became nullable on the model
            # (e.g. Admin.password_hash once accounts stopped requiring a
            # local password) needs its NOT NULL constraint relaxed too —
            # ADD COLUMN above only handles columns that don't exist yet.
            existing_column_info = {col["name"]: col for col in inspector.get_columns(table.name)}
            for column in table.columns:
                info = existing_column_info.get(column.name)
                if info is None:
                    continue  # just added above, already matches the model
                if column.nullable and not info["nullable"]:
                    conn.execute(
                        text(f"ALTER TABLE {table.name} ALTER COLUMN {column.name} DROP NOT NULL")
                    )
                    print(f"Relaxed NOT NULL on {table.name}.{column.name}")


def sync_missing_indexes() -> None:
    """Add indexes present on the ORM models but missing from deployed tables.

    create_all() only creates indexes when it creates the table itself; it
    never alters a table that's already there (same gap sync_missing_columns()
    covers for columns). Runs CREATE INDEX CONCURRENTLY so building the index
    on a large existing table doesn't hold a lock against writes.
    """
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                continue  # just created by create_missing_tables()

            existing_indexes = {ix["name"] for ix in inspector.get_indexes(table.name)}
            for index in table.indexes:
                if index.name in existing_indexes:
                    continue

                index_ddl = str(CreateIndex(index).compile(dialect=engine.dialect))
                index_ddl = re.sub(r"^CREATE( UNIQUE)? INDEX", r"CREATE\1 INDEX CONCURRENTLY", index_ddl)
                conn.execute(text(index_ddl))
                print(f"Added missing index {index.name} on {table.name}")


def bootstrap_initial_admin() -> None:
    """Add the first onyen to the accounts allowlist so someone can log in via SSO.

    No password: accounts are provisioned by onyen and authenticate through
    UNC's Onyen SSO (or the dev-only bypass login outside production).
    """
    email = os.getenv("INITIAL_ADMIN_EMAIL")
    onyen = os.getenv("INITIAL_ADMIN_ONYEN")
    first_name = os.getenv("INITIAL_ADMIN_FIRST_NAME", "Initial")
    last_name = os.getenv("INITIAL_ADMIN_LAST_NAME", "Admin")
    role = os.getenv("INITIAL_ADMIN_ROLE", "admin")

    if not email and not onyen:
        print("No initial admin requested")
        return

    if not email or not onyen:
        print("INITIAL_ADMIN_EMAIL and INITIAL_ADMIN_ONYEN must be set together")
        sys.exit(1)

    try:
        onyen = validate_onyen(onyen)
    except ValueError as exc:
        print(str(exc))
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
    sync_missing_columns()
    sync_missing_indexes()
    bootstrap_initial_admin()
    print("Database initialization complete")
