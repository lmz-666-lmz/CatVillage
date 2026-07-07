from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status

from app.core.config import UPLOAD_MAX_BYTES


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

class StorageService:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file: UploadFile, sub_dir: str = "") -> str:
        extension = Path(file.filename or "").suffix.lower()
        if not extension:
            extension = ".jpg"
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unsupported image format")
        
        filename = f"{uuid4().hex}{extension}"
        
        target_dir = self.upload_dir
        if sub_dir:
            target_dir = target_dir / sub_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
        target_path = target_dir / filename

        bytes_written = 0
        with target_path.open("wb") as output:
            while True:
                chunk = file.file.read(1024 * 1024)
                if not chunk:
                    break
                bytes_written += len(chunk)
                if bytes_written > UPLOAD_MAX_BYTES:
                    target_path.unlink(missing_ok=True)
                    raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="uploaded file too large")
                output.write(chunk)

        if sub_dir:
            return f"/api/v1/uploads/{sub_dir}/{filename}"
        return f"/api/v1/uploads/{filename}"

UPLOAD_ROOT = Path(__file__).resolve().parents[2] / "uploads"
storage_service = StorageService(UPLOAD_ROOT)
