from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile, status

from app.core.config import UPLOAD_MAX_BYTES


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 安全的文件删除基础目录
_STORAGE_ROOT = Path(__file__).resolve().parents[2]
_SAFE_DELETE_ROOTS = {
    _STORAGE_ROOT / "storage",
    _STORAGE_ROOT / "uploads",
}

def safe_delete_file(file_path: str | None) -> bool:
    """安全删除 storage/uploads 目录内由项目生成的文件。

    返回 True 表示已删除，False 表示文件不存在或跳过。
    绝不根据用户传入路径直接 rm，防止路径穿越。
    """
    if not file_path:
        return False
    try:
        resolved = Path(file_path).resolve()
    except (OSError, ValueError):
        return False

    # 路径安全校验：必须在允许的目录内
    allowed = False
    for root in _SAFE_DELETE_ROOTS:
        try:
            resolved.relative_to(root)
            allowed = True
            break
        except ValueError:
            continue

    if not allowed:
        print(f"[safe_delete] 拒绝删除非项目文件: {file_path}")
        return False

    try:
        if resolved.is_file():
            resolved.unlink()
            return True
    except OSError as exc:
        print(f"[safe_delete] 删除文件失败: {file_path}, 错误: {exc}")
    return False

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
