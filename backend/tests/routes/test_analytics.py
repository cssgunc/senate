"""Integration tests for POST /api/analytics/pageview (issue #206)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
import app.routers.analytics as analytics_router
from app.database import get_db
from app.main import app
from app.models.base import Base
from app.models.PageView import PageView

_SQLITE_URL = "sqlite:///:memory:"


@pytest.fixture()
def write_engine():
    engine = create_engine(_SQLITE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def write_client(write_engine):
    TestSession = sessionmaker(bind=write_engine)

    def _override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c, TestSession
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(autouse=True)
def clear_ingest_rate_limits(monkeypatch):
    analytics_router._ingest_requests.clear()
    monkeypatch.setattr(analytics_router, "ANALYTICS_INGEST_SECRET", "test-ingest-secret")
    yield
    analytics_router._ingest_requests.clear()


_PAYLOAD = {
    "path": "/about",
    "referrer_host": "google.com",
    "user_agent": "pytest-agent",
    "visitor_hash": "abc123",
}


class TestCreatePageview:
    def test_rejects_when_not_configured(self, write_client, monkeypatch):
        client, _ = write_client
        monkeypatch.setattr(analytics_router, "ANALYTICS_INGEST_SECRET", None)
        resp = client.post(
            "/api/analytics/pageview", json=_PAYLOAD, headers={"X-Analytics-Secret": "anything"}
        )
        assert resp.status_code == 503

    def test_rejects_missing_secret(self, write_client):
        client, _ = write_client
        resp = client.post("/api/analytics/pageview", json=_PAYLOAD)
        assert resp.status_code == 401

    def test_rejects_wrong_secret(self, write_client):
        client, _ = write_client
        resp = client.post(
            "/api/analytics/pageview", json=_PAYLOAD, headers={"X-Analytics-Secret": "wrong"}
        )
        assert resp.status_code == 401

    def test_accepts_correct_secret(self, write_client):
        client, _ = write_client
        resp = client.post(
            "/api/analytics/pageview",
            json=_PAYLOAD,
            headers={"X-Analytics-Secret": "test-ingest-secret"},
        )
        assert resp.status_code == 204

    def test_persists_pageview_row(self, write_client):
        client, TestSession = write_client
        client.post(
            "/api/analytics/pageview",
            json=_PAYLOAD,
            headers={"X-Analytics-Secret": "test-ingest-secret"},
        )
        db = TestSession()
        try:
            rows = db.query(PageView).all()
            assert len(rows) == 1
            assert rows[0].path == "/about"
            assert rows[0].referrer_host == "google.com"
            assert rows[0].visitor_hash == "abc123"
        finally:
            db.close()

    def test_missing_required_field_returns_422(self, write_client):
        client, _ = write_client
        bad = {k: v for k, v in _PAYLOAD.items() if k != "visitor_hash"}
        resp = client.post(
            "/api/analytics/pageview", json=bad, headers={"X-Analytics-Secret": "test-ingest-secret"}
        )
        assert resp.status_code == 422

    def test_rate_limit_enforced(self, write_client, monkeypatch):
        client, _ = write_client
        monkeypatch.setattr(analytics_router, "RATE_LIMIT_MAX_REQUESTS", 2)

        headers = {"X-Analytics-Secret": "test-ingest-secret"}
        for _ in range(2):
            resp = client.post("/api/analytics/pageview", json=_PAYLOAD, headers=headers)
            assert resp.status_code == 204

        resp = client.post("/api/analytics/pageview", json=_PAYLOAD, headers=headers)
        assert resp.status_code == 429
