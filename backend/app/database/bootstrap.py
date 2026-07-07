from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import ADMIN_PASSWORD, ADMIN_USERNAME
from app.core.security import get_password_hash
from app.database.session import Base, engine
from app.models.user import User
import app.models


def ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        if engine.dialect.name == "sqlite":
            columns = connection.execute(text("PRAGMA table_info(users)")).fetchall()
            column_names = {row[1] for row in columns}
            if "nickname" not in column_names:
                connection.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(100)"))
            if "avatar_url" not in column_names:
                connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url TEXT"))
            if "is_admin" not in column_names:
                connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
            connection.execute(text("UPDATE users SET nickname = username WHERE nickname IS NULL OR TRIM(nickname) = ''"))
            return

        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN nickname VARCHAR(100)"))
        except Exception:
            pass
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url TEXT"))
        except Exception:
            pass
        try:
            connection.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"))
        except Exception:
            pass
        connection.execute(text("UPDATE users SET nickname = username WHERE nickname IS NULL OR TRIM(nickname) = ''"))


def seed_admin_user(db: Session) -> bool:
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        return False
    if "replace-with" in ADMIN_PASSWORD or "your-admin-password" in ADMIN_PASSWORD or len(ADMIN_PASSWORD) < 6:
        return False

    user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
    if user is None:
        user = User(
            id=str(uuid4()),
            username=ADMIN_USERNAME,
            nickname=ADMIN_USERNAME,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            is_active=True,
            is_admin=True,
        )
        db.add(user)
    else:
        user.is_active = True
        user.is_admin = True
    db.commit()
    return True
