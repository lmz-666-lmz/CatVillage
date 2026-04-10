from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text

from app.database.session import Base


class AIChatHistory(Base):
    __tablename__ = "ai_chat_histories"

    id = Column(String(50), primary_key=True, index=True)
    pet_id = Column(String(50), index=True, comment="猫咪ID")
    user_id = Column(String(50), index=True, comment="用户ID")
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), comment="创建时间")