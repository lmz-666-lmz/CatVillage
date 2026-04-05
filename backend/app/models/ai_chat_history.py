from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.database.session import Base


class AIChatHistory(Base):
    __tablename__ = "ai_chat_histories"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    pet_id = Column(String(64), ForeignKey("cat_profiles.id"), nullable=False, index=True)
    user_id = Column(String(64), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)