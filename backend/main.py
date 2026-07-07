from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1 import ai_assistant
from app.api.v1 import admin
from app.api.v1 import auth
from app.api.v1 import emotions
from app.api.v1 import health
from app.api.v1 import message
from app.api.v1 import social
from app.api.v1 import doctors
from app.api.v1 import vision
from app.api.v1.pet_profiles import router as pet_profiles_router
from app.core.config import get_cors_origins
from app.database.bootstrap import ensure_schema, seed_admin_user
from app.database.session import SessionLocal
import app.models


app = FastAPI(title="CatVillage API", version="v1")

cors_origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials="*" not in cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(admin.router)
app.include_router(pet_profiles_router, prefix="/api/v1")
app.include_router(emotions.router)
app.include_router(ai_assistant.router)
app.include_router(health.router)
app.include_router(social.router, prefix="/api/v1")
app.include_router(message.router)
app.include_router(doctors.router)
app.include_router(vision.router)

UPLOAD_ROOT = Path(__file__).resolve().parent / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "online"}


@app.on_event("startup")
def on_startup() -> None:
    try:
        ensure_schema()
        db = SessionLocal()
        try:
            seed_admin_user(db)
        finally:
            db.close()
    except Exception as exc:
        print(f"database initialization skipped: {exc}")
