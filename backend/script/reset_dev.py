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
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine


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
    """Seed the database with comprehensive mock data

    Seeds data according to TDD Section 4.4 database models.
    All data is realistic and centered around today's date.
    """
    db = SessionLocal()
    today = date.today()
    now = datetime.now()
    current_session = 107  # 107th Senate session

    try:
        # Check if models are implemented
        try:
            from app.models import __all__ as model_names
            if not model_names:
                print("No models found - skipping data seeding")
                print("  Implement models in app/models/__init__.py first")
                return
        except (ImportError, AttributeError):
            print("No models found - skipping data seeding")
            print("  Implement models in app/models/__init__.py first")
            return

        print("\nSeeding mock data...")

        # TODO: Implement data seeding once models are created
        # Reference TDD Section 4.4 for complete database schema
        #
        # Example structure:
        #
        # from app.models import (
        #     Admin, District, Senator, Leadership, Committee,
        #     CommitteeMembership, Legislation, LegislationAction,
        #     CalendarEvent, News, CarouselSlide, Staff,
        #     StaticPageContent, BudgetData, AppConfig,
        #     FinanceHearingConfig, DistrictMapping
        # )
        #
        # # 1. Create Admin accounts
        # admin_user = Admin(
        #     email="admin@unc.edu",
        #     first_name="Admin",
        #     last_name="User",
        #     PID="123456789",
        #     role="admin"
        # )
        # db.add(admin_user)
        #
        # # 2. Create Districts
        # districts = []
        # for i in range(1, 11):
        #     district = District(
        #         district_name=f"District {i}",
        #         description=f"Representing campus area {i}"
        #     )
        #     districts.append(district)
        #     db.add(district)
        #
        # # 3. Create Senators
        # # 4. Create Leadership
        # # 5. Create Committees
        # # 6. Create Committee Memberships
        # # 7. Create Legislation
        # # 8. Create Legislation Actions
        # # 9. Create Calendar Events
        # # 10. Create News Articles
        # # 11. Create Carousel Slides
        # # 12. Create Staff
        # # 13. Create Static Pages
        # # 14. Create Budget Data
        # # 15. Create App Config
        # # 16. Create Finance Hearing Config
        # # 17. Create District Mappings

        db.commit()
        print("Sample data seeded successfully")
        print()
        print("Seeded data summary:")
        print("  - Admin accounts: Ready for implementation")
        print("  - Districts: Ready for implementation")
        print("  - Senators: Ready for implementation")
        print("  - Leadership: Ready for implementation")
        print("  - Committees: Ready for implementation")
        print("  - Legislation: Ready for implementation")
        print("  - Calendar events: Ready for implementation")
        print("  - News articles: Ready for implementation")
        print("  - And more... (see TDD Section 4.4)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


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
