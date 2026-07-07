from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.database.session import Base


class CatProfile(Base):
    __tablename__ = "cat_profiles"

    id = Column(String(64), primary_key=True, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    breed = Column(String(100), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    avatar_url = Column(String(255), nullable=True)
    is_neutered = Column(Boolean, nullable=False, default=False)
    medical_history = Column(Text, nullable=True)
    vaccine_status = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
