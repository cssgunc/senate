"""Create database and tables

This script creates the main development database according to the TDD spec (Section 4.4).
It should be run once during initial setup or when resetting the development environment.

Usage:
    python -m script.create_db
"""

import sys

import pyodbc

from app.database import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, Base, engine


def create_database():
    """Create the database if it doesn't exist"""
    print(f"Connecting to SQL Server at {DB_HOST}:{DB_PORT}...")

    # Connect to master database to create our database
    master_conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={DB_HOST},{DB_PORT};"
        f"DATABASE=master;"
        f"UID={DB_USER};"
        f"PWD={DB_PASSWORD};"
        f"TrustServerCertificate=yes"
    )

    try:
        conn = pyodbc.connect(master_conn_str)
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{DB_NAME}'")
        if cursor.fetchone():
            print(f"Database '{DB_NAME}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            print(f"Database '{DB_NAME}' created successfully")

        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print(f"Error connecting to SQL Server: {e}")
        print("\nMake sure:")
        print("  - SQL Server is running (check docker-compose)")
        print("  - Connection details are correct")
        print(f"  - Server: {DB_HOST}:{DB_PORT}")
        print(f"  - User: {DB_USER}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error creating database: {e}")
        sys.exit(1)


def create_tables():
    """Create all tables defined in models

    Tables are created according to the database schema in TDD Section 4.4:
    - Admin
    - News
    - Senator
    - Leadership
    - Committee
    - CommitteeMembership
    - Legislation
    - LegislationAction
    - CalendarEvent
    - CarouselSlide
    - FinanceHearingConfig
    - FinanceHearingDate
    - Staff
    - District
    - DistrictMapping
    - StaticPageContent
    - BudgetData
    - AppConfig

    Note: Models must be implemented in app/models/__init__.py first.
    """
    try:
        # Import all models to ensure they're registered with Base
        # This import will fail gracefully if models aren't implemented yet
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
        print(
            "\nIf you see 'no such table' errors, make sure models are defined in app/models/__init__.py"
        )
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
