import os
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


def _get_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


@lru_cache
def get_cors_origins() -> list[str]:
    raw_origins = os.getenv("CORS_ORIGINS", "")
    origins = [item.strip() for item in raw_origins.split(",") if item.strip()]
    return origins or ["http://localhost:5173", "http://127.0.0.1:5173"]


DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "").strip()
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com").strip()
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat").strip()
DB_POOL_SIZE = _get_int_env("DB_POOL_SIZE", 3)
DB_MAX_OVERFLOW = _get_int_env("DB_MAX_OVERFLOW", 2)
DB_POOL_RECYCLE = _get_int_env("DB_POOL_RECYCLE", 1800)
UPLOAD_MAX_BYTES = _get_int_env("UPLOAD_MAX_BYTES", 10 * 1024 * 1024)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()
