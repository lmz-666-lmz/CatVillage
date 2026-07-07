from sqlalchemy import Boolean, Column, DateTime, String, Text, func

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar_url = Column(Text, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
