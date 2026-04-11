from pathlib import Path

from sqlalchemy import text

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1 import auth
from app.api.v1 import ai_assistant
from app.api.v1 import emotions
from app.api.v1 import health
from app.api.v1 import message
from app.api.v1 import social
from app.api.v1.pet_profiles import router as pet_profiles_router
from app.database.session import Base, engine
import app.models

app = FastAPI(title="CatVillage API", version="v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(pet_profiles_router, prefix="/api/v1")
app.include_router(emotions.router)
app.include_router(ai_assistant.router)
app.include_router(health.router)
app.include_router(social.router, prefix="/api/v1")
app.include_router(message.router)

UPLOAD_ROOT = Path(__file__).resolve().parent / "uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
app.mount("/api/v1/uploads", StaticFiles(directory=str(UPLOAD_ROOT)), name="uploads")


def migrate_ai_chat_histories_schema() -> None:
    if engine.dialect.name != 'mssql':
        return

    with engine.begin() as connection:
        migration_needed = connection.execute(
            text(
                """
                SELECT COUNT(1)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = 'ai_chat_histories'
                  AND COLUMN_NAME IN ('id', 'pet_id', 'user_id')
                  AND DATA_TYPE NOT IN ('nvarchar', 'varchar', 'nchar', 'char', 'text', 'ntext')
                """
            )
        ).scalar_one()

        if migration_needed == 0:
            return

        connection.execute(
            text(
                """
                IF OBJECT_ID('dbo.ai_chat_histories_new', 'U') IS NOT NULL
                    DROP TABLE dbo.ai_chat_histories_new;

                CREATE TABLE dbo.ai_chat_histories_new (
                    id NVARCHAR(50) NOT NULL,
                    pet_id NVARCHAR(50) NULL,
                    user_id NVARCHAR(50) NULL,
                    question NVARCHAR(MAX) NOT NULL,
                    answer NVARCHAR(MAX) NOT NULL,
                    created_at DATETIME2 NOT NULL CONSTRAINT DF_ai_chat_histories_new_created_at DEFAULT SYSDATETIME(),
                    CONSTRAINT PK_ai_chat_histories_new PRIMARY KEY (id)
                );

                INSERT INTO dbo.ai_chat_histories_new (id, pet_id, user_id, question, answer, created_at)
                SELECT
                    CAST(id AS NVARCHAR(50)),
                    CAST(pet_id AS NVARCHAR(50)),
                    CAST(user_id AS NVARCHAR(50)),
                    question,
                    answer,
                    COALESCE(CAST(created_at AS DATETIME2), SYSDATETIME())
                FROM dbo.ai_chat_histories;

                IF OBJECT_ID('dbo.ai_chat_histories_legacy', 'U') IS NOT NULL
                    DROP TABLE dbo.ai_chat_histories_legacy;

                EXEC sp_rename 'dbo.ai_chat_histories', 'ai_chat_histories_legacy';
                EXEC sp_rename 'dbo.ai_chat_histories_new', 'ai_chat_histories';

                DROP TABLE dbo.ai_chat_histories_legacy;
                """
            )
        )


def migrate_users_nickname_column() -> None:
    with engine.begin() as connection:
        if engine.dialect.name == "mssql":
            has_nickname = connection.execute(
                text(
                    """
                    SELECT COUNT(1)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'nickname'
                    """
                )
            ).scalar_one()

            if has_nickname == 0:
                connection.execute(text("ALTER TABLE users ADD nickname NVARCHAR(100) NULL"))

            connection.execute(
                text(
                    """
                    UPDATE users
                    SET nickname = username
                    WHERE nickname IS NULL OR LTRIM(RTRIM(nickname)) = ''
                    """
                )
            )
            return

        if engine.dialect.name == "sqlite":
            columns = connection.execute(text("PRAGMA table_info(users)")).fetchall()
            has_nickname = any(row[1] == "nickname" for row in columns)
            if not has_nickname:
                connection.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(100)"))
            connection.execute(text("UPDATE users SET nickname = username WHERE nickname IS NULL OR TRIM(nickname) = ''"))
            return

        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(100)"))
        except Exception:
            pass
        connection.execute(text("UPDATE users SET nickname = username WHERE nickname IS NULL OR TRIM(nickname) = ''"))


@app.get("/")
def root() -> dict[str, str]:
    return {"status": "online"}


@app.on_event("startup")
def on_startup() -> None:
    try:
        migrate_users_nickname_column()
        migrate_ai_chat_histories_schema()
        Base.metadata.create_all(bind=engine)
    except Exception as exc:
        print(f"database initialization skipped: {exc}")
