"""Admin upload endpoints for image assets."""

from io import BytesIO
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import MAX_UPLOAD_SIZE_BYTES, UPLOAD_BASE_URL, UPLOAD_DIR
from app.dependencies.auth import get_current_user
from app.models import Admin

router = APIRouter(prefix="/api/admin", tags=["admin-upload"])

_ALLOWED_FORMATS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def _validate_and_load_image(content: bytes) -> tuple[Image.Image, str]:
    """Validate uploaded bytes as a supported image and return image + extension."""
    if len(content) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="File too large. Max size is 5MB")

    try:
        image = Image.open(BytesIO(content))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(status_code=400, detail="Unsupported file type") from exc

    fmt = (image.format or "").upper()
    if fmt not in _ALLOWED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    return image, _ALLOWED_FORMATS[fmt]


def _save_resized_images(image: Image.Image, extension: str) -> str:
    """Save standard and thumbnail variants and return the main filename."""
    uploads_dir = Path(UPLOAD_DIR)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    base_name = uuid4().hex
    main_filename = f"{base_name}.{extension}"
    thumb_filename = f"{base_name}_thumb.{extension}"

    save_kwargs: dict[str, int | bool] = {}
    if extension in {"jpg", "webp"}:
        save_kwargs["quality"] = 90
    if extension == "jpg":
        save_kwargs["optimize"] = True

    working = image.convert("RGB") if extension == "jpg" else image.copy()

    standard = working.copy()
    if standard.width > 800:
        ratio = 800 / standard.width
        resized_height = round(standard.height * ratio)
        standard = standard.resize((800, resized_height), Image.Resampling.LANCZOS)
    standard.save(uploads_dir / main_filename, **save_kwargs)

    thumb = ImageOps.fit(working.copy(), (150, 150), method=Image.Resampling.LANCZOS)
    thumb.save(uploads_dir / thumb_filename, **save_kwargs)

    return main_filename


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: Admin = Depends(get_current_user),
):
    """Upload an image and return a relative URL to the resized standard image."""
    _ = current_user
    content = await file.read()
    image, extension = _validate_and_load_image(content)
    filename = _save_resized_images(image, extension)
    return {"url": f"{UPLOAD_BASE_URL}/{filename}"}
