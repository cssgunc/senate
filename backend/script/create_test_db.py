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

import pyodbc

from app.database import DB_HOST, DB_PASSWORD, DB_PORT, DB_USER

TEST_DB_NAME = "senate_test"


def create_test_database():
    """Create the test database if it doesn't exist

    Creates a separate database for testing according to TDD Section 4.3.
    Test database uses the same schema as development but is populated
    with test fixtures rather than seed data.
    """
    print(f"Connecting to SQL Server at {DB_HOST}:{DB_PORT}...")

    # Connect to master database to create test database
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
        cursor.execute(f"SELECT database_id FROM sys.databases WHERE name = '{TEST_DB_NAME}'")
        if cursor.fetchone():
            print(f"Test database '{TEST_DB_NAME}' already exists")
        else:
            cursor.execute(f"CREATE DATABASE {TEST_DB_NAME}")
            print(f"Test database '{TEST_DB_NAME}' created successfully")

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
