"""Reset development database with fresh data

This script resets the development database and populates it with realistic
mock data for testing and development. All date-based data is centered around
today's date for realistic testing.

Usage:
    python -m script.reset_dev

Warning:
    This script DROPS ALL TABLES and recreates them from scratch.
    All existing data will be lost. Only use this in development.

Data seeded (based on TDD Section 4.4):
    - Admin accounts (admin and staff roles)
    - Districts and district mappings
    - Senators (current and past sessions)
    - Leadership positions
    - Committees and memberships
    - Legislation with actions
    - Calendar events
    - News articles
    - Carousel slides
    - Staff directory
    - Static page content
    - Budget data
    - Finance hearing config
    - App configuration
"""

import sys
from datetime import datetime

from app.database import Base, engine
from script.seed_data import run_seed


def reset_database():
    """Drop all tables and recreate them"""
    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped")
    except Exception as e:
        print(f"Error dropping tables: {e}")
        sys.exit(1)

    print("\nCreating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        print("\nMake sure models are implemented in app/models/__init__.py")
        sys.exit(1)


def seed_data():
    """Seed the database with comprehensive mock data."""
    try:
        run_seed()
    except Exception as e:
        print(f"Error seeding data: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Resetting Development Database")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print()
    print("WARNING: This will DELETE ALL existing data!")
    print()

    # Confirmation in interactive mode
    if sys.stdin.isatty():
        response = input("Are you sure you want to continue? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("Operation cancelled.")
            sys.exit(0)
        print()

    reset_database()
    seed_data()

    print()
    print("=" * 60)
    print("Development Database Reset Complete!")
    print("=" * 60)
    print()
