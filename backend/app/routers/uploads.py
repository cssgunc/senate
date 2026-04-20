"""Public file-serving endpoints for uploaded images."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import UPLOAD_DIR

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


@router.get("/{filename}")
def get_uploaded_file(filename: str):
    """Serve files from the configured upload directory."""
    if Path(filename).name != filename:
        raise HTTPException(status_code=404, detail="File not found")

    filepath = (Path(UPLOAD_DIR) / filename).resolve()
    uploads_root = Path(UPLOAD_DIR).resolve()

    if uploads_root not in filepath.parents and filepath != uploads_root:
        raise HTTPException(status_code=404, detail="File not found")

    if not filepath.exists() or not filepath.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(filepath)
