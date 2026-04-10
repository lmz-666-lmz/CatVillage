import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile

class StorageService:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file: UploadFile, sub_dir: str = "") -> str:
        extension = Path(file.filename or "").suffix.lower()
        if not extension:
            extension = ".jpg"
        
        filename = f"{uuid4().hex}{extension}"
        
        target_dir = self.upload_dir
        if sub_dir:
            target_dir = target_dir / sub_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
        target_path = target_dir / filename

        with target_path.open("wb") as output:
            shutil.copyfileobj(file.file, output)

        if sub_dir:
            return f"/api/v1/uploads/{sub_dir}/{filename}"
        return f"/api/v1/uploads/{filename}"

UPLOAD_ROOT = Path(__file__).resolve().parents[3] / "uploads"
storage_service = StorageService(UPLOAD_ROOT)
