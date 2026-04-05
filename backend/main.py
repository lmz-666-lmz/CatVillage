import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth
from app.api.v1 import ai_assistant
from app.api.v1 import emotions
from app.api.v1 import health
from app.api.v1 import message
from app.api.v1 import social
from app.api.v1.pet_profiles import router as pet_profiles_router
from app.database.session import Base, engine
import app.models

app = FastAPI()

cors_origins = os.getenv("CORS_ORIGINS")
if cors_origins:
    allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
else:
    allow_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(pet_profiles_router, prefix="/api/v1")
app.include_router(emotions.router)
app.include_router(ai_assistant.router)
app.include_router(health.router)
app.include_router(social.router)
app.include_router(message.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "online"}


@app.on_event("startup")
def on_startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"database initialization skipped: {exc}")
