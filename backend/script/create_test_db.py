"""Create test database

This script creates a separate test database for running pytest tests.
The test database is isolated from the development database to prevent
test data from polluting the development environment.

Usage:
    python -m script.create_test_db

Environment:
    Set DB_NAME=senate_test when running tests to use this database.
"""

import sys

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from app.database import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER

TEST_DB_NAME = "senate_test"


def create_test_database():
    """Create the test database if it doesn't exist"""
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

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (TEST_DB_NAME,))
        if cursor.fetchone():
            print(f"Test database '{TEST_DB_NAME}' already exists")
        else:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(TEST_DB_NAME)))
            print(f"Test database '{TEST_DB_NAME}' created successfully")

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
        print(f"Unexpected error creating test database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("Creating Test Database")
    print("=" * 60)
    print()

    create_test_database()

    print()
    print("=" * 60)
    print("Test Database Setup Complete!")
    print("=" * 60)
    print()
    print("Usage:")
    print("  Set environment variable: DB_NAME=senate_test")
    print("  Run tests with: pytest")
    print()
    print("Note:")
    print("  Test database uses the same models as development")
    print("  Tables will be created/dropped by pytest fixtures")
    print()
