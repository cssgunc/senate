"""Test fixtures for integration tests using an in-memory SQLite database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 — ensures all models register with Base.metadata
from app.database import Base, get_db
from app.main import app

SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture()
def db_session():
    """Provide a transactional SQLite in-memory session, rolled back after each test."""
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def integration_client(db_session):
    """FastAPI test client with the DB dependency overridden to use SQLite."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.pop(get_db, None)
