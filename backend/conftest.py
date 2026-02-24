"""Root conftest for backend tests.

Provides shared fixtures available to all test files.
Database-dependent fixtures are gated behind the 'integration' marker
so unit tests can run without a SQL Server connection (e.g., in CI).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture()
def client():
    """FastAPI test client (no DB required). This can be removed upon actual test implementations."""
    return TestClient(app)
