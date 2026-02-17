"""Tests for main application and health endpoints."""


def test_root(client):
    """Root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Senate API"
    assert "version" in data


def test_health_check(client):
    """Health check returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_cors_headers(client):
    """CORS middleware allows frontend origin."""
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_unknown_route_returns_404(client):
    """Non-existent routes return 404."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
