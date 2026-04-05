from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.database.session import Base


class EmotionRecord(Base):
    __tablename__ = "emotion_records"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pet_id = Column(String(64), ForeignKey("cat_profiles.id"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    label = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=True)
    raw_result = Column(Text, nullable=True)
    record_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)