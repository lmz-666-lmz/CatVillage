from sqlalchemy import Boolean, Column, String

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    nickname = Column(String(100), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)