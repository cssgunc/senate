from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models.Senator import Senator

client = TestClient(app)


@pytest.fixture
def mock_send_email():
    with patch("app.routers.contact.send_email") as mock_func:
        yield mock_func


@pytest.fixture
def mock_db_session():
    mock_session = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.clear()


def test_contact_speaker_success(mock_send_email, mock_db_session):
    payload = {
        "name": "Jane Tarheel",
        "email": "jane@unc.edu",
        "message": "We need more funds for our club!",
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

    mock_send_email.assert_called_once()
    args = mock_send_email.call_args.kwargs
    assert args["to_email"] == "speaker@unc.edu"


def test_contact_specific_senator(mock_send_email, mock_db_session):
    # Setup test DB senator output
    senator = Senator(
        id=99,
        first_name="John",
        last_name="Doe",
        email="jonny.senator@unc.edu",
        district=1,
        is_active=True,
        session_number=105,
    )
    mock_db_session.query.return_value.filter.return_value.first.return_value = senator

    payload = {
        "name": "Bill Blank",
        "email": "bill@unc.edu",
        "message": "Hello Senator!",
        "senator_id": 99,
    }
    response = client.post("/api/contact", json=payload)
    assert response.status_code == 200

    mock_send_email.assert_called_once()
    args = mock_send_email.call_args.kwargs
    assert args["to_email"] == "jonny.senator@unc.edu"


def test_contact_with_zero_senator_id_returns_404(mock_send_email, mock_db_session):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    payload = {
        "name": "Zero Case",
        "email": "zero@unc.edu",
        "message": "Attempting senator lookup with id 0",
        "senator_id": 0,
    }

    response = client.post("/api/contact", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Senator not found"
    mock_send_email.assert_not_called()


def test_rate_limiting():
    from app.routers.contact import ip_logs

    ip_logs.clear()

    payload = {"name": "Spammer", "email": "spam@spam.com", "message": "Buy my links"}

    for _ in range(5):
        res = client.post("/api/contact", json=payload)
        assert res.status_code == 200

    res = client.post("/api/contact", json=payload)
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["detail"]
