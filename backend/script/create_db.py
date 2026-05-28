"""Create database and tables

This script creates the main development database if it doesn't exist.
It should be run once during initial setup or when resetting the development environment.

Usage:
    python -m script.create_db
"""

import sys

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.database import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, Base, engine


def create_database():
    """Create the database if it doesn't exist"""
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}...")

    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            dbname="postgres",
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        if cursor.fetchone():
            print(f"Database '{DB_NAME}' already exists")
        else:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully")

        cursor.close()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        print("\nMake sure:")
        print("  - PostgreSQL is running (check docker-compose)")
        print("  - Connection details are correct")
        print(f"  - Server: {DB_HOST}:{DB_PORT}")
        print(f"  - User: {DB_USER}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error creating database: {e}")
        sys.exit(1)


def create_tables():
    """Create all tables defined in models"""
    try:
        try:
            from app.models import __all__ as model_names

            if model_names:
                print(f"Found {len(model_names)} model(s) to create")
        except (ImportError, AttributeError):
            print("No models found in app/models/__init__.py")
            print("  Tables will be created once models are implemented")
            return

        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")

    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Development Database")
    print("=" * 60)
    print()

    create_database()
    print()
    create_tables()
    print()

    print("=" * 60)
    print("Database Setup Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  Run 'python -m script.reset_dev' to seed with sample data")
    print()
