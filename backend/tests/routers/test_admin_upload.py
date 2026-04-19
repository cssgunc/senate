from io import BytesIO

import pytest
from PIL import Image

from app.dependencies.auth import get_current_user
from app.main import app
from app.models import Admin


@pytest.fixture
def admin_client(client, test_db, seeded_admins):
    admin = seeded_admins["admin"]

    def _override_current_user():
        return test_db.query(Admin).filter(Admin.id == admin.id).first()

    app.dependency_overrides[get_current_user] = _override_current_user
    yield client
    app.dependency_overrides.pop(get_current_user, None)


def _make_png_bytes(width: int = 1000, height: int = 600) -> bytes:
    image = Image.new("RGB", (width, height), color="red")
    buf = BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def test_valid_upload(admin_client, tmp_path, monkeypatch):
    from app.routers import uploads as uploads_router
    from app.routers.admin import upload as upload_router

    monkeypatch.setattr(upload_router, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(upload_router, "UPLOAD_BASE_URL", "/api/uploads")
    monkeypatch.setattr(uploads_router, "UPLOAD_DIR", str(tmp_path))

    payload = _make_png_bytes()
    response = admin_client.post(
        "/api/admin/upload",
        files={"file": ("headshot.png", payload, "image/png")},
    )

    assert response.status_code == 200
    body = response.json()
    assert "url" in body
    assert body["url"].startswith("/api/uploads/")

    filename = body["url"].split("/")[-1]
    assert (tmp_path / filename).exists()
    assert (tmp_path / f"{filename.rsplit('.', 1)[0]}_thumb.{filename.rsplit('.', 1)[1]}").exists()

    get_response = admin_client.get(body["url"])
    assert get_response.status_code == 200


def test_invalid_file_type(admin_client, tmp_path, monkeypatch):
    from app.routers.admin import upload as upload_router

    monkeypatch.setattr(upload_router, "UPLOAD_DIR", str(tmp_path))

    response = admin_client.post(
        "/api/admin/upload",
        files={"file": ("notes.txt", b"this-is-not-an-image", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported file type"


def test_oversized_file(admin_client, tmp_path, monkeypatch):
    from app.routers.admin import upload as upload_router

    monkeypatch.setattr(upload_router, "UPLOAD_DIR", str(tmp_path))

    oversized = b"x" * (5 * 1024 * 1024 + 1)
    response = admin_client.post(
        "/api/admin/upload",
        files={"file": ("big.png", oversized, "image/png")},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "File too large. Max size is 5MB"
